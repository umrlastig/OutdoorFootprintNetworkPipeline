# -*- coding: utf-8 -*-

'''
    Calculs des cartes de densités, de constraste et binaire
    A lancer dans la console QGIS

'''

import sys
import csv
csv.field_size_limit(sys.maxsize)
import math
import os
import psycopg2
from scipy.ndimage import maximum_filter

import tracklib as tkl
from tracklib.util.qgis import QGIS, LineStyle, PointStyle
from . import plotRaster, styleTurbo

try:
    from qgis.PyQt.QtCore import QVariant
    from qgis.core import QgsStyle, QgsColorRampShader, QgsColorRampShader, QgsRasterShader
    from qgis.core import QgsSingleBandPseudoColorRenderer, QgsRasterLayer, QgsProject
    from qgis.core import QgsCoordinateReferenceSystem, QgsVectorLayer, QgsFeatureRequest
    from qgis.core import QgsField, QgsGeometry, QgsFeature, QgsVectorFileWriter
    from PyQt5.QtGui import QColor
    import processing
    from qgis.core import edit
except ImportError:
    print ('Code running in a no qgis environment')




def density(RESPATH, G1_SIZE, G2_SIZE, SEUIL):


    respath = RESPATH + 'image/'


    # =============================================================================
    #       Chargement des traces GPS
    #  Ici elles sont mises dans un fichier CSV dont la géométrie de la trace est
    #  dans le format WKT

    fmt = tkl.TrackFormat({'ext': 'CSV',
                           'srid': 'ENU',
                           'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                           'separator': ';',
                           'header': 1})
    
    cptId = 1
    resampledtracespath = RESPATH + 'resample/'
    collection = tkl.TrackReader.readFromFile(resampledtracespath, fmt)
    for trace in collection:
        trace.uid = cptId
        trace.tid = cptId
        cptId += 1
    print ('Number of tracks : ', collection.size())

    QGIS.plotTracks(collection, type='POINT',
                    style=PointStyle.circleYellow,
                    title='Zone3-walk points')
    QGIS.plotTracks(collection, type='LINE',
                    style=LineStyle.simpleLightOrange,
                    title='Zone3-walk line')



    # =============================================================================
    #       Calcul des densités des traces GPS


    af_algos = ['uid']
    cell_operators = [tkl.co_count_distinct]

    marge = 0
    resolutionG1 = (G1_SIZE, G1_SIZE)
    bbox = collection.bbox()

    rasterG1 = tkl.summarize(collection, af_algos, cell_operators, resolutionG1, marge,
                   align=tkl.BBOX_ALIGN_CENTER)
    grilleG1 = rasterG1.getAFMap('uid#co_count_distinct')
    for i in range(grilleG1.raster.nrow):
        for j in range(grilleG1.raster.ncol):
            grilleG1.grid[i][j] = grilleG1.grid[i][j] / (G1_SIZE*G1_SIZE)
    
    pathG1 = respath + 'G1.asc'
    tkl.RasterWriter.writeMapToAscFile(pathG1, grilleG1)
    
    plotRaster(pathG1, "G1", "Turbo")
    
    # Combien de cellules de chaque côté pour la petite résolution ?
    nb = math.floor(G2_SIZE / G1_SIZE)


    # =============================================================================
    
    epsilon = 0.001
    # On construit une grille vide comme G1
    box = tkl.Bbox(tkl.ENUCoords(rasterG1.xmin, rasterG1.ymin),
                   tkl.ENUCoords(rasterG1.xmax, rasterG1.ymax))
    res = rasterG1.resolution
    margin = 0
    align = tkl.BBOX_ALIGN_CENTER
    rasterK = tkl.Raster(bbox=box, resolution=res, margin=margin, align=align)
    rasterK.addAFMap('K')


    G2 = maximum_filter(grilleG1.grid, size=nb)
    
    for i in range(rasterK.nrow):
        for j in range(rasterK.ncol):
            x = rasterK.xmin + j * res[0] + 1
            y = rasterK.ymin - (i - rasterK.nrow + 1) * res[1] + 1
            (column, line) = rasterG1.getCell(tkl.ENUCoords(x, y))
            g1 = grilleG1.grid[line][column]
    
            g2 = G2[line][column] / (nb * G1_SIZE * nb * G1_SIZE)
    
            if g1 <= 2:
                g1 = 0
    
            if g2 <= 0:
                g2 = epsilon
    
            k = g1 / g2
    
            rasterK.getAFMap(0).grid[i][j] = k
    
    grilleK = rasterK.getAFMap(0)
    
    pathK = respath + 'K.asc'
    tkl.RasterWriter.writeMapToAscFile(pathK, grilleK)
    
    plotRaster(pathK, "K", "Turbo")


    # =============================================================================
    
    # On construit une grille vide comme G1
    box = tkl.Bbox(tkl.ENUCoords(rasterK.xmin, rasterK.ymin),
                   tkl.ENUCoords(rasterK.xmax, rasterK.ymax))
    res = rasterK.resolution
    margin = 0
    align = tkl.BBOX_ALIGN_CENTER
    raster = tkl.Raster(bbox=box, resolution=res, margin=margin, align=align)
    raster.addAFMap('B')
    
    for i in range(raster.nrow):
        for j in range(raster.ncol):
            v = grilleK.grid[i][j]
            if v > SEUIL:
                raster.getAFMap(0).grid[i][j] = 1
            else:
                raster.getAFMap(0).grid[i][j] = 0
    
    pathB = respath + 'B.asc'
    tkl.RasterWriter.writeMapToAscFile(pathB, raster.getAFMap(0))
    
    plotRaster(pathB, "B")


    # =============================================================================
    
    
    print ("Fin des calculs des cartes de densités, de constraste et binaire.")
    
    
    print ("END SCRIPT 2.")



def polygonize(RESPATH, SEUIL_SURFACE, connectparam):

    respath  = RESPATH + 'image/'

    pathB           = respath + 'B.asc'
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

    connection = psycopg2.connect(
        host=connectparam['HOST'],
        port = connectparam['PORT'],
        database=connectparam['DATABASE'],
        user=connectparam['USER'],
        password=connectparam['PASSWD']
    )

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


