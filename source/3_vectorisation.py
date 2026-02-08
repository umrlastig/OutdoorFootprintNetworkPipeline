# -*- coding: utf-8 -*-


import psycopg2
import tracklib as tkl

'''
    
    Travail sur l'image
    - Filtre morphologique : dilatation puis erosion 
    - Vectorisation
    - Squeletisation : center line dans Postgis

    A lancer dans la console QGIS + connection à Postgis

'''


SEUIL_SURFACE = 5000 # m2

HOST     = 'localhost'
PORT     = 5433
DATABASE = 'test'
USER     = 'test'
PASSWD   = 'test'

respath  = r'/home/md_vandamme/4_RESEAU/ExampleTest/densite/'

pathB = respath + 'B.asc'

patherosion     = respath + 'erosion.tif'
roadsurfpath    = respath + 'road_surface.shp'
squelettepath   = respath + 'squelette.shp'


try:
    os.remove(roadsurfpath)
    os.remove(patherosion)
    os.remove(squelettepath)
    print(f"Files '{roadsurfpath}', '{patherosion}' and '{squelettepath}' deleted successfully.")
except FileNotFoundError:
    print(f"File '{roadsurfpath}', '{patherosion}' or '{squelettepath}' not found.")



# =============================================================================

def plotRaster(pathres, title):
    layerGrid = QgsRasterLayer(pathres, title, "gdal")
    layerGrid.setCrs(QgsCoordinateReferenceSystem("EPSG:2154"))
    QgsProject.instance().addMapLayer(layerGrid)



# =============================================================================
#   On charge le binaire

rasterB = tkl.RasterReader.readFromAscFile(pathB, name='B', separator='\t')
grille = rasterB.getAFMap('B')
plotRaster(pathB, "B")


# =============================================================================
#   Fermeture
'''
ALGORITHM :
    - 0: Dilation
    - 1: Erosion
    - 2: Closing
    - 3: Opening
'''

param = {
    'INPUT': pathB,
    'DIMENSION': 0,
    'ALGORITHM': 1,
    'STRUCTURE':'[[0, 1, 0],\n[1, 1, 1],\n[0, 1, 0]]',
    'ORIGIN': '0, 0',
    'BANDSTATS': True,
    'DTYPE': 0,
    'OUTPUT' : patherosion,
    'ITERATIONS': 1,
    'BORDERVALUE': 0,
    'MASK': None
}
resultat = processing.run("scipy_filters:binary_morphology", param)
plotRaster(patherosion, "erosion")



# =============================================================================
#   Vectorisation

param = {
    'INPUT':patherosion,
    'BAND':1,
    'FIELD':'DN',
    'EIGHT_CONNECTEDNESS':False,
    'EXTRA':'',
    'OUTPUT': roadsurfpath
}

resultat = processing.run("gdal:polygonize", param)
layerRoadSurface = QgsVectorLayer(roadsurfpath, "Road surface", "ogr")
layerRoadSurface.setCrs(QgsCoordinateReferenceSystem("EPSG:2154"))
QgsProject.instance().addMapLayer(layerRoadSurface)


request = QgsFeatureRequest().setFilterExpression("DN = 0")
with edit(layerRoadSurface):
    for feat in layerRoadSurface.getFeatures(request):
        layerRoadSurface.deleteFeature(feat.id())


# -----------------------------------------------------------------------------
#     On ajoute un champ surface pour garder les troncons
#          dont la surface est supérieure à un certain seuil

# On regarde si l'attribut existe dans la couche
pr = layerRoadSurface.dataProvider()
trouve = False
for attribut in pr.fields():
    if attribut.name() == ' SURF':
        print (attribut.name())
        trouve = True

# S'il n'existe pas, on le crée
if not trouve :
    layerRoadSurface.startEditing()
    pr.addAttributes([QgsField("SURF", QVariant.Double)])
layerRoadSurface.updateFields()
layerRoadSurface.commitChanges()


attrSurf = layerRoadSurface.fields().lookupField("SURF")

with edit(layerRoadSurface):
    for feat in layerRoadSurface.getFeatures():
        surf = feat.geometry().area()
        layerRoadSurface.changeAttributeValue(feat.id(), attrSurf, float(surf))



# =============================================================================
#   Squeletisation : center line dans Postgis


layerSqueletteBrut = QgsVectorLayer("LineString?crs=epsg:2154", "Squelette brut", "memory")
pr = layerSqueletteBrut.dataProvider()
layerSqueletteBrut.startEditing()

connection = psycopg2.connect(host=HOST, port = PORT,
                        database=DATABASE, user=USER, password=PASSWD)

for feat in layerRoadSurface.getFeatures():
    surf = feat.geometry().area()
    if surf > SEUIL_SURFACE:
        wkt = feat.geometry().asWkt()
        cursor = connection.cursor()
        sql = " SELECT ST_ASText(ST_ApproximateMedialAxis(ST_BUFFER(ST_GeomFromText('" + wkt + "'), 0.25))) as ligne "
        cursor.execute(sql)
        record = cursor.fetchone()
        mlwkt = record[0]

        ligne = QgsGeometry.fromWkt(mlwkt)

        newFeature = QgsFeature()
        newFeature.setGeometry(ligne)
        pr.addFeature(newFeature)

connection.close()
layerSqueletteBrut.commitChanges()
QgsProject.instance().addMapLayer(layerSqueletteBrut)

save_options = QgsVectorFileWriter.SaveVectorOptions()
save_options.driverName = "ESRI Shapefile"
save_options.fileEncoding = "UTF-8"

error = QgsVectorFileWriter.writeAsVectorFormatV3(layerSqueletteBrut,
                                                  squelettepath,
                                                  QgsProject.instance().transformContext(),
                                                  save_options)






# =============================================================================


print ("Fin des calculs des cartes de densités, de constraste et binaire.")


print ("END SCRIPT 3.")






