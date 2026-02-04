# -*- coding: utf-8 -*-


import psycopg2

'''
    
    Travail sur l'image
    - Filtre morphologique : dilatation puis erosion 
    - Vectorisation
    - Squeletisation : center line dans Postgis

    A lancer dans la console QGIS + connection à Postgis

'''


# On supprime toutes les couches du projet
QgsProject.instance().removeAllMapLayers()

SEUIL_SURFACE = 5000 # m2

HOST     = 'localhost'
PORT     = 5433
DATABASE = 'test'
USER     = 'test'
PASSWD   = 'test'

ascpath      = r'/home/md_vandamme/4_RESEAU/V2/zone1/zone1_B_V1.asc'
closingpath  = r'/home/md_vandamme/4_RESEAU/V2/zone1/b_fermeture.tif'
roadsurfpath = r'/home/md_vandamme/4_RESEAU/V2/zone1/road_surface.shp'

try:
    os.remove(roadsurfpath)
    print(f"File '{roadsurfpath}' deleted successfully.")
except FileNotFoundError:
    print(f"File '{roadsurfpath}' not found.")



# =============================================================================

def plotRaster(pathres, title):

    layerGrid = QgsRasterLayer(pathres, title, "gdal")
    layerGrid.setCrs(QgsCoordinateReferenceSystem("EPSG:2154"))
    QgsProject.instance().addMapLayer(layerGrid)



# =============================================================================
#   On charge le binaire

rasterB = tkl.RasterReader.readFromAscFile(ascpath, name='B', separator='\t')
grille = rasterB.getAFMap('B')

plotRaster(ascpath, "B")


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
    'INPUT': ascpath,
    'DIMENSION': 0,
    'ALGORITHM': 0, # fermeture
    'STRUCTURE':'[[0, 1, 0],\n[1, 1, 1],\n[0, 1, 0]]',
    # [[1, 1, 1],\n[1, 1, 1],\n[1, 1, 1]]
    #'STRUCTURE':'[[0, 0, 1, 0, 0],\n[0, 1, 1, 1, 0],\n[1, 1, 1, 1, 1],\n[0, 1, 1, 1, 0],\n[0, 0, 1, 0, 0]]',
    'ORIGIN': '0, 0',
    'BANDSTATS': True,
    'DTYPE': 0,
    'OUTPUT':closingpath,
    'ITERATIONS': 1,
    'BORDERVALUE': 0,
    'MASK': None
}
resultat = processing.run("scipy_filters:binary_morphology", param)
# pathRasterFermeture = resultat['OUTPUT']
plotRaster(closingpath, "Fermeture")



# =============================================================================
#   Vectorisation

param = {
    'INPUT':closingpath,
    'BAND':1,
    'FIELD':'DN',
    'EIGHT_CONNECTEDNESS':False,
    'EXTRA':'',
    'OUTPUT': roadsurfpath
}

resultat = processing.run("gdal:polygonize", param)
layerRoadSurface = QgsVectorLayer(roadsurfpath, "Réseau mobilité surface vectorielle", "ogr")
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


connection = psycopg2.connect(host=HOST, port = PORT,
                        database=DATABASE, user=USER, password=PASSWD)

for feat in layerRoadSurface.getFeatures():
    surf = feat.geometry().area()
    if surf > SEUIL_SURFACE:
        wkt = feat.geometry().asWkt()
        cursor = connection.cursor()
        sql = "SELECT ST_ASText(ST_ApproximateMedialAxis(ST_GeomFromText('" + wkt + "'))) as ligne "
        cursor.execute(sql)
        record = cursor.fetchone()
        mlwkt = record[0]
        # lines = wkt.loads(mlwkt)
        print ('---')

connection.close()






