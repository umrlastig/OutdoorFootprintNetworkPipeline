# -*- coding: utf-8 -*-

# Trouver les points des traces qui ne sont pas appariées
#    + trouver les points qui n'ont pas servi
# On les prend si ce sont des bonnes traces


import math
import os
import sys
import csv
csv.field_size_limit(sys.maxsize)

import tracklib as tkl

from scipy.ndimage import maximum_filter
import numpy as np
from osgeo import gdal, ogr, osr
from tracklib.util.centerline import Shp2centerline



def second_round(RESPATH, NB_OBS_MIN, G1_SIZE, G2_SIZE):

    RESAMPLE_SIZE_GRID = 1
    SEUIL = 350

    SEUIL_SURFACE = 750

    buffer_size = 5
    k = 0.6

    # =========================================================================
    #   Lecture des traces découpées et ré-échantillonnées.
    #
    '''
    fmt = tkl.TrackFormat({'ext': 'CSV',
                           'srid': 'ENU',
                           'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                           'time_fmt': '2D/2M/4Y 2h:2m:2s',
                           'separator': ';',
                           'header': 0,
                           'cmt': '#',
                           'read_all': True})
    tracespath = RESPATH + '/resample_fusion/'
    collection2 = tkl.TrackReader.readFromFile(tracespath, fmt)
    print ('Nombre de traces:', collection2.size())
    '''
    collection = tkl.TrackCollection()
    mmtrackpath = RESPATH + '/mapmatch/tmm/'
    for mmfilename in os.listdir(mmtrackpath):
        #N;E;time;U;num;track_id;user_id;hmm_inference;mmtype;idedge
        fmt = tkl.TrackFormat({'ext': 'CSV',
                               'srid': 'ENU',
                               'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                               'separator': ';',
                               'header': 0,
                               'comment': '#',
                               'read_all': True})
        trace = tkl.TrackReader.readFromFile(mmtrackpath + mmfilename, fmt)
        collection.addTrack(trace)
        # print (trace.size(), type(trace))
    print ('Nombre de traces:', collection.size())

    index =  tkl.SpatialIndex(collection)
    # neighborhood(coord, unit)


    cpt = 1
    morceaux = tkl.TrackCollection()
    for i in range(collection.size()):
        track = collection.getTrack(i)
        pkid = track.tid
        # print (pkid)

        num = track.getObsAnalyticalFeature('num', 0)
        track_id = track.getObsAnalyticalFeature('track_id', 0)
        user_id = track.getObsAnalyticalFeature('user_id', 0)
        #version = track.getObsAnalyticalFeature('version', 0)

        cptNot = 0
        morceau = tkl.Track()
        morceau.tid = cpt
        morceau.uid = cpt
        cpt += 1
        for j in range(track.size()):
            obs = track.getObs(j)
            if str(track["mmtype", j]) == "NOT":
                cptNot += 1

                # On modifie un petit peu la position
                POINTS = index.neighborhood(obs.position, None, buffer_size)
                # TODO : il faudrait trouver le barycentre et faire le kième de la distance encore
                # print (len(POINTS))

                morceau.addObs(obs.copy())
            else:
                if cptNot >= NB_OBS_MIN:
                    morceau.resample(RESAMPLE_SIZE_GRID, mode=tkl.MODE_SPATIAL)
                    morceaux.addTrack(morceau)
                morceau = tkl.Track()
                morceau.tid = cpt
                morceau.uid = cpt
                cpt += 1
                cptNot = 0

        if cptNot >= NB_OBS_MIN:
            morceaux.addTrack(morceau)


    # On enregistre
    print (morceaux.size())
    '''
    tracespath = RESPATH + "points_left/"
    tkl.TrackWriter.writeToFiles(morceaux, tracespath,
                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                 h=1, separator=";") # af_names=af_names


    # =========================================================================
    af_algos = ['uid']
    cell_operators = [tkl.co_count_distinct]

    marge = 0
    resolutionG1 = (G1_SIZE, G1_SIZE)
    bbox = collection.bbox()

    rasterG1 = tkl.summarize(morceaux, af_algos, cell_operators, resolutionG1, marge,
                   align=tkl.BBOX_ALIGN_CENTER)
    grilleG1 = rasterG1.getAFMap('uid#co_count_distinct')
    for i in range(grilleG1.raster.nrow):
        for j in range(grilleG1.raster.ncol):
            grilleG1.grid[i][j] = grilleG1.grid[i][j] / (G1_SIZE*G1_SIZE)
    
    pathG1 = RESPATH + 'image/G1_ST.asc'
    tkl.RasterWriter.writeMapToAscFile(pathG1, grilleG1)



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
    
            if g1 <= 0.5:
                g1 = 0
    
            if g2 <= 0:
                g2 = epsilon
    
            k = g1 / g2
    
            rasterK.getAFMap(0).grid[i][j] = k
    
    grilleK = rasterK.getAFMap(0)
    
    pathK = RESPATH + 'image/K_ST.asc'
    tkl.RasterWriter.writeMapToAscFile(pathK, grilleK)
    
    #plotRaster(pathK, "K", "Turbo")


    # =========================================================================

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
    
    pathB = RESPATH + 'image/B_ST.asc'
    tkl.RasterWriter.writeMapToAscFile(pathB, raster.getAFMap(0))
    
    # plotRaster(pathB, "B")

    print ("Fin des calculs des cartes de densités, de constraste et binaire.")


    # =========================================================================



    patherosion     = RESPATH + 'image/erosion_ST.tif'
    pathdilatation  = RESPATH + 'image/dilatation_ST.tif'
    surfpath        = RESPATH + 'image/surface_ST.shp'
    roadsurfpath    = RESPATH + 'image/road_surface_ST.shp'
    squelettepath   = RESPATH + 'network/squelette_ST.shp'

    


    # =============================================================================
    #   On charge le binaire

    rasterB = tkl.RasterReader.readFromAscFile(pathB, name='B', separator='\t')
    mapBinaire = rasterB.getAFMap('B')


    # =============================================================================
    #   Dilatation + Fermeture

    mask = np.array([
        [0,1,0],
        [1,1,1],
        [0,1,0]])
    # Dilatation
    mapBinaire.filter(mask, np.max)
    tkl.RasterWriter.writeMapToAscFile(pathdilatation, mapBinaire)
    #pathdilatation = patherosion

    # Erosion
    mask = np.array([
        [0,0,1,0,0],
        [0,1,1,1,0],
        [1,1,1,1,1],
        [0,1,1,1,0],
        [0,0,1,0,0]])
    mapBinaire.filter(np.array([[1]]), lambda x : 1-x)     # Dual de la carte
    mapBinaire.filter(mask, np.max)                        # Dilatation
    mapBinaire.filter(np.array([[1]]), lambda x : 1-x)     # Dual de la carte
    tkl.RasterWriter.writeMapToAscFile(patherosion, mapBinaire)


    pathdepart = patherosion

    # =============================================================================
    #   Vectorisation

    #  get raster datasource
    src_ds = gdal.Open(pathdepart)
    srcband = src_ds.GetRasterBand(1)

    dst_layername = 'road_surface'
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dst_ds = driver.CreateDataSource(surfpath)
    sp_ref = osr.SpatialReference()
    sp_ref.SetFromUserInput('EPSG:2154')

    dst_layer = dst_ds.CreateLayer(dst_layername, srs=sp_ref)
    fld2 = ogr.FieldDefn("DN", ogr.OFTInteger)
    dst_layer.CreateField(fld2)
    dst_field = dst_layer.GetLayerDefn().GetFieldIndex("DN")

    gdal.Polygonize(srcband, None, dst_layer, dst_field, [], callback=None )


    # Nettoyage
    del src_ds
    del dst_ds


    # On copie
    src_surf = ogr.Open(surfpath)
    driver.CopyDataSource(src_surf, roadsurfpath)
    src_surf = None






    # =============================================================================
    #   Squeletisation : DN=0 + filtre sur la surface + id

    src_ds = ogr.Open(roadsurfpath, 1)
    src_layer = src_ds.GetLayer()


    # Appliquer un filtre attributaire
    src_layer.SetAttributeFilter("DN = 0")

    # Récupérer les features à supprimer
    feature_ids = []
    for feature in src_layer:
        feature_ids.append(feature.GetFID())
    
    # Supprimer les features
    for fid in feature_ids:
        src_layer.DeleteFeature(fid)

    src_layer.SetAttributeFilter(None)

    # ------------------------------------------
    #   Surface

    fids_to_delete = []

    for feature in src_layer:
        geom = feature.GetGeometryRef()
        if geom is not None:
            area = geom.GetArea()
            if area <= SEUIL_SURFACE:
                fids_to_delete.append(feature.GetFID())
            else:
                print (area, SEUIL_SURFACE)

    for fid in fids_to_delete:
        src_layer.DeleteFeature(fid)

    del src_ds


    # -----------------------------------------
    #   Id

    ds = ogr.Open(roadsurfpath, 1)
    layer = ds.GetLayer()

    # Vérifier si le champ existe déjà
    layer_defn = layer.GetLayerDefn()
    field_names = [layer_defn.GetFieldDefn(i).GetName() for i in range(layer_defn.GetFieldCount())]

    if "id" not in field_names:
        field_defn = ogr.FieldDefn("id", ogr.OFTInteger)
        layer.CreateField(field_defn)

    i = 1
    for feature in layer:
        feature.SetField("id", i)
        layer.SetFeature(feature)
        i += 1

    ds = None




    # =============================================================================
    #   Squeletisation : center line

    interp_dist = 5
    clean_dist  = 0

    Shp2centerline(roadsurfpath, squelettepath, interp_dist, clean_dist)
    

    '''


