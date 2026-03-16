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
from scipy.ndimage import maximum_filter

import tracklib as tkl
import numpy as np

from osgeo import gdal, ogr, osr
from pipeline import Shp2centerline





def density_polygonize(RESPATH, G1_SIZE, G2_SIZE, SEUIL, SEUIL_SURFACE, prefix='PT',
                       rep='resample_grid'):

    main_text   = "----------------------------------------------------------------------\r\n"
    main_text  += "STAGE 2 :                                   \r\n"
    main_text  += "   - Calcul d’une carte de densité à partir des traces GNSS \r\n"
    main_text  += "   - De la vectorisation on extrait une ligne centrée ≡ arc de la topologie \r\n"
    main_text  += "----------------------------------------------------------------------\r\n"
    print(main_text, end='')


    respath = RESPATH + 'image/'


    # =============================================================================
    #       Chargement des traces GPS
    #  Ici elles sont mises dans un fichier CSV dont la géométrie de la trace est
    #  dans le format WKT

    fmt = tkl.TrackFormat({'ext': 'CSV',
                           'srid': 'ENU',
                           'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                           'separator': ';',
                           'header': 1,
                           'read_all': True})
    
    resampledtracespath = RESPATH + rep + '/'
    collection = tkl.TrackReader.readFromFile(resampledtracespath, fmt)
    for trace in collection:
        trace.uid = trace.getObsAnalyticalFeature('user_id', 0)
        trace.tid = trace.getObsAnalyticalFeature('track_id', 0)
    print ('Number of tracks : ', collection.size())



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
    
    pathG1 = respath + 'G1_' + prefix + '.asc'
    tkl.RasterWriter.writeMapToAscFile(pathG1, grilleG1)
    


    # =============================================================================

    # Combien de cellules de chaque côté pour la petite résolution ?
    nb = math.floor(G2_SIZE / G1_SIZE)

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
            #g2 = G2[line][column] / (G2_SIZE * G2_SIZE)
    
            if g1 < 2:
                g1 = 0
    
            if g2 <= 0:
                g2 = epsilon
    
            k = g1 / g2
    
            rasterK.getAFMap(0).grid[i][j] = k
    
    grilleK = rasterK.getAFMap(0)
    
    pathK = respath + 'K_' + prefix + '.asc'
    tkl.RasterWriter.writeMapToAscFile(pathK, grilleK)
    
    #plotRaster(pathK, "K", "Turbo")


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
    
    pathB = respath + 'B_' + prefix + '.asc'
    tkl.RasterWriter.writeMapToAscFile(pathB, raster.getAFMap(0))
    
    print ("Fin des calculs des cartes de densités, de constraste et binaire.")
    

    # =========================================================================


    pathB             = respath + 'B_' + prefix + '.asc'
    patherosion       = respath + 'erosion_' + prefix + '.tif'
    pathdilatation    = respath + 'dilatation_' + prefix + '.tif'
    surfpath          = respath + 'surface_' + prefix + '.shp'
    roadsurfpath      = respath + 'road_surface_' + prefix + '.shp'
    roadsurflissepath = respath + 'road_surface_lissee_' + prefix + '.shp'
    squelettepath     = RESPATH + 'network/squelette_' + prefix + '.shp'

    try:
        os.remove(patherosion)
        os.remove(pathdilatation)
        print(f"Files '{patherosion}' and '{pathdilatation}' deleted successfully.")
    except FileNotFoundError:
        print(f"File '{patherosion}' or '{pathdilatation}' not found.")

    try:
        os.remove(respath + 'road_surface_' + prefix + '.shp')
        os.remove(respath + 'road_surface_' + prefix + '.shx')
        os.remove(respath + 'road_surface_' + prefix + '.dbf')
        os.remove(respath + 'road_surface_' + prefix + '.prj')
        print(f"Files road_surface.shp deleted successfully.")
    except FileNotFoundError:
        print(f"File '{roadsurfpath}' not found.")

    try:
        os.remove(respath + 'road_surface_lissee_' + prefix + '.shp')
        os.remove(respath + 'road_surface_lissee_' + prefix + '.shx')
        os.remove(respath + 'road_surface_lissee_' + prefix + '.dbf')
        print(f"Files road_surface_lissee.shp deleted successfully.")
    except FileNotFoundError:
        print(f"File '{roadsurflissepath}' not found.")

    try:
        os.remove(respath + 'surface_' + prefix + '.shp')
        os.remove(respath + 'surface_' + prefix + '.shx')
        os.remove(respath + 'surface_' + prefix + '.dbf')
        os.remove(respath + 'surface_' + prefix + '.prj')
        print(f"Files surface.shp deleted successfully.")
    except FileNotFoundError:
        print(f"File '{roadsurfpath}' not found.")

    try:
        os.remove(RESPATH + 'network/squelette_' + prefix + '.shp')
        os.remove(RESPATH + 'network/squelette_' + prefix + '.shx')
        os.remove(RESPATH + 'network/squelette_' + prefix + '.dbf')
        os.remove(RESPATH + 'network/squelette_' + prefix + '.cpg')
        print(f"Files '{squelettepath}' deleted successfully.")
    except FileNotFoundError:
        print(f"File '{squelettepath}' not found.")



    # =============================================================================
    #   On charge le binaire

    rasterB = tkl.RasterReader.readFromAscFile(pathB, name='B', separator='\t')
    mapBinaire = rasterB.getAFMap('B')


    # =============================================================================
    #   Dilatation + Erosion

    mask = np.array([
        [0,1,0],
        [1,1,1],
        [0,1,0]])
    # Dilatation
    mapBinaire.filter(mask, np.max)
    tkl.RasterWriter.writeMapToAscFile(pathdilatation, mapBinaire)
    #pathdilatation = patherosion

    # Erosion
    '''
    mask = np.array([
        [0,0,1,0,0],
        [0,1,1,1,0],
        [1,1,1,1,1],
        [0,1,1,1,0],
        [0,0,1,0,0]])
    '''
    mapBinaire.filter(np.array([[1]]), lambda x : 1-x)     # Dual de la carte
    mapBinaire.filter(mask, np.max)                        # Dilatation
    mapBinaire.filter(np.array([[1]]), lambda x : 1-x)     # Dual de la carte
    tkl.RasterWriter.writeMapToAscFile(patherosion, mapBinaire)


    pathdepart = patherosion

    # =========================================================================
    #   Vectorisation dans le layer surface

    shpDriver = ogr.GetDriverByName("ESRI Shapefile")
    dsSurface = shpDriver.CreateDataSource(surfpath)

    l93Ref = osr.SpatialReference()
    l93Ref.SetFromUserInput('EPSG:2154')

    surfaceLayername = 'surface'
    layerSurface = dsSurface.CreateLayer(surfaceLayername, srs=l93Ref)

    fld2 = ogr.FieldDefn("DN", ogr.OFTInteger)
    layerSurface.CreateField(fld2)
    dst_field = layerSurface.GetLayerDefn().GetFieldIndex("DN")

    #  get raster datasource
    dsDepart = gdal.Open(pathdepart)
    srcband = dsDepart.GetRasterBand(1)

    gdal.Polygonize(srcband, None, layerSurface, dst_field, [], callback=None)

    # Nettoyage
    del dsSurface
    del dsDepart


    # =========================================================================
    # On copie Surface vers RoadSurface

    # ouvrir la source
    dsSurface = ogr.Open(surfpath)

    # copier la datasource
    dsRoadSurface = shpDriver.CopyDataSource(dsSurface, roadsurfpath)

    # fermer les datasets
    dsSurface = None
    dsRoadSurface = None


    # =============================================================================
    #   Squeletisation : DN=0 + filtre sur la surface + id

    dsRoadSurface = ogr.Open(roadsurfpath, 1)
    layerRoadSurface = dsRoadSurface.GetLayer()


    # Appliquer un filtre attributaire
    layerRoadSurface.SetAttributeFilter("DN = 0")

    # Récupérer les features à supprimer
    feature_ids = []
    for feature in layerRoadSurface:
        feature_ids.append(feature.GetFID())
    
    # Supprimer les features
    for fid in feature_ids:
        layerRoadSurface.DeleteFeature(fid)

    layerRoadSurface.SetAttributeFilter(None)

    # ------------------------------------------

    fids_to_delete = []

    for feature in layerRoadSurface:
        geom = feature.GetGeometryRef()
        if geom is not None:
            area = geom.GetArea()
            if area <= SEUIL_SURFACE:
                fids_to_delete.append(feature.GetFID())
            else:
                print ("Un pplygone gardé avec comme surface", area, SEUIL_SURFACE)

    for fid in fids_to_delete:
        layerRoadSurface.DeleteFeature(fid)



    # -----------------------------------------
    #   Id


    # Vérifier si le champ existe déjà
    layer_defn = layerRoadSurface.GetLayerDefn()
    field_names = [layer_defn.GetFieldDefn(i).GetName() for i in range(layer_defn.GetFieldCount())]

    if "id" not in field_names:
        field_defn = ogr.FieldDefn("id", ogr.OFTInteger)
        layerRoadSurface.CreateField(field_defn)

    i = 1
    for feature in layerRoadSurface:
        feature.SetField("id", i)
        layerRoadSurface.SetFeature(feature)
        i += 1

    dsRoadSurface = None



    # =========================================================================
    #   Lissage du polygone pour oublier le profil en escalier


    #filtre(roadsurfpath, roadsurflissepath, shpDriver)
    dual(roadsurfpath, roadsurflissepath, shpDriver)


    # =========================================================================
    #   Squeletisation : centerline

    interp_dist = 5
    clean_dist  = 0

    Shp2centerline(roadsurflissepath, squelettepath, interp_dist, clean_dist)
    


    # =========================================================================


    print ("Fin des calculs de vectorisation et squelette.")



def dual(roadsurfpath, roadsurflissepath, shpDriver):
    dsRoadSurface = ogr.Open(roadsurfpath, 0)
    layerRoadSurface = dsRoadSurface.GetLayer()

    srs = layerRoadSurface.GetSpatialRef()

    dsRoadSurfaceLissee = shpDriver.CreateDataSource(roadsurflissepath)
    layerRoadSurfaceLissee = dsRoadSurfaceLissee.CreateLayer(
        "road_surface_lissee",
        srs,
        geom_type = ogr.wkbPolygon
    )

    # copier les champs attributaires
    src_defn = layerRoadSurface.GetLayerDefn()
    for i in range(src_defn.GetFieldCount()):
        field_defn = src_defn.GetFieldDefn(i)
        layerRoadSurfaceLissee.CreateField(field_defn)

    dst_defn = layerRoadSurfaceLissee.GetLayerDefn()

    for feature in layerRoadSurface:
        geom = feature.GetGeometryRef().Clone()
        if geom is None:
            continue

        polygon = ogr.Geometry(ogr.wkbPolygon)
        for i in range(geom.GetGeometryCount()):
            ring = geom.GetGeometryRef(i)
            nbpoints = ring.GetPointCount()

            track = tkl.Track()
            for p in range(0, nbpoints):
                track.addObs(tkl.Obs(tkl.ENUCoords(ring.GetPoint(p)[0], ring.GetPoint(p)[1]), tkl.ObsTime()))
            tdual = track.dual()
            newring = ogr.Geometry(ogr.wkbLinearRing)
            for o in tdual:
                newring.AddPoint(o.position.getX(), o.position.getY())
            newring.CloseRings()
            polygon.AddGeometry(newring)
    
        # Créer une nouvelle feature
        dst_feat = ogr.Feature(dst_defn)
        
        # Copier les attributs
        for i in range(dst_defn.GetFieldCount()):
            dst_feat.SetField(i, feature.GetField(i))
        
        # Assigner la géométrie
        dst_feat.SetGeometry(polygon)
        
        # Ajouter au layer
        layerRoadSurfaceLissee.CreateFeature(dst_feat)
        
        dst_feat = None


    dsRoadSurface = None
    dsRoadSurfaceLissee = None


def filtre(roadsurfpath, roadsurflissepath, shpDriver):
    dsRoadSurface = ogr.Open(roadsurfpath, 0)
    layerRoadSurface = dsRoadSurface.GetLayer()

    dsRoadSurfaceLissee = shpDriver.CreateDataSource(roadsurflissepath)
    layerRoadSurfaceLissee = dsRoadSurfaceLissee.CreateLayer(
        "Road surface lissee",
        geom_type = layerRoadSurface.GetGeomType()
    )

    # copier les champs attributaires
    src_defn = layerRoadSurface.GetLayerDefn()
    for i in range(src_defn.GetFieldCount()):
        field_defn = src_defn.GetFieldDefn(i)
        layerRoadSurfaceLissee.CreateField(field_defn)

    dst_defn = layerRoadSurfaceLissee.GetLayerDefn()

    for feature in layerRoadSurface:
        geom = feature.GetGeometryRef()

        polygon = ogr.Geometry(ogr.wkbPolygon)
        for i in range(geom.GetGeometryCount()):
            ring = geom.GetGeometryRef(i)
            nbpoints = ring.GetPointCount()
            # print ('Nb of vertex : ', nbpoints)

            newring = ogr.Geometry(ogr.wkbLinearRing)
            newring.AddPoint(ring.GetPoint(0)[0], ring.GetPoint(0)[1])
            for p in range(1, nbpoints-1):
                lon = 0.5*ring.GetPoint(p)[0] + 0.25*ring.GetPoint(p-1)[0] + 0.25*ring.GetPoint(p+1)[0]
                lat = 0.5*ring.GetPoint(p)[1] + 0.25*ring.GetPoint(p-1)[1] + 0.25*ring.GetPoint(p+1)[1]
                newring.AddPoint(lon, lat)
            newring.AddPoint(ring.GetPoint(nbpoints-1)[0], ring.GetPoint(nbpoints-1)[1])
            polygon.AddGeometry(newring)
    
        # Créer une nouvelle feature
        dst_feat = ogr.Feature(dst_defn)
        
        # Copier les attributs
        for i in range(dst_defn.GetFieldCount()):
            dst_feat.SetField(i, feature.GetField(i))
        
        # Assigner la géométrie
        dst_feat.SetGeometry(polygon)
        
        # Ajouter au layer
        layerRoadSurfaceLissee.CreateFeature(dst_feat)
        
        dst_feat = None


    dsRoadSurface = None
    dsRoadSurfaceLissee = None


