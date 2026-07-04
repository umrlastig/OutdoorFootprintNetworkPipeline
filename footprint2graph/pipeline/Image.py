# -*- coding: utf-8 -*-

'''
    Calculs des cartes de densités, de constraste et binaire
    A lancer dans la console QGIS

'''

import math
import os
import time
import sys

import csv
csv.field_size_limit(sys.maxsize)

import numpy as np
# from scipy.ndimage import maximum_filter
from skimage.morphology import remove_small_holes, remove_small_objects
from skimage.measure import label, regionprops

import fiona
from osgeo import gdal, ogr, osr

import tracklib as tkl
from footprint2graph import Shp2centerline
from footprint2graph import log_event


'''
Ce module

-  Calcul d’une carte de densité à partir des traces GNSS
-  De la vectorisation on extrait une ligne centrée ≡ arc de la topologie


'''

def density_polygonize(RESPATH, G1_SIZE, G2_SIZE, SEUIL_DENSITE, SEUIL_SURFACE,
                       pipeline_idx = None,
                       cut_factor=5, interp_dist=5, clean_dist=0,
                       log_level = 'ERROR'):

    idx = int (pipeline_idx)

    print("Starting rasterization and vectorization (iteration " + str(idx) + ") \n")

    respath = RESPATH + 'image/'

    prefix = str(idx)
    if idx == 1:
        rep = 'resample_grid'
    else:
        rep = 'points_not_mm_' + prefix


    if log_level == 'ERROR':
        verbose = False
    else:
        verbose = True


    # =============================================================================
    #       Chargement des traces GPS
    #  Ici elles sont mises dans un fichier CSV dont la géométrie de la trace est
    #  dans le format WKT

    if log_level == 'INFO' or log_level == 'DEBUG':
        print ('    Loading tracks from : ', rep)
    t0 = time.time()

    fmt = tkl.TrackFormat({'ext': 'CSV',
                           'srid': 'ENU',
                           'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                           'separator': ';',
                           'header': 1,
                           'read_all': True})
    
    resampledtracespath = RESPATH + rep + '/'
    # tracks = tkl.TrackReader.readFromFile(resampledtracespath, fmt, verbose=verbose)
    tracks = tkl.TrackSource(resampledtracespath, fmt)

    total = len(tracks)
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ('    Number of tracks to load: ', total)


    #  On calcule la bbox
    bbox = None
    cpt = 1
    for track in tracks:

        if cpt%1000 == 0 and (log_level == 'INFO' or log_level == 'DEBUG'):
            print ('        ', cpt, '/', total)
        cpt += 1

        if bbox is None:
            bbox = track.bbox()
        else:
            bbox = bbox + track.bbox()


    # =========================================================================
    #      On construit G1

    if log_level == 'INFO' or log_level == 'DEBUG':
        print ('    Building high-resolution geometry density grid G1 : ', G1_SIZE, 'm ...')


    margin = 0
    resolutionG1 = (G1_SIZE, G1_SIZE)

    rasterG1 = tkl.Raster(bbox=bbox, resolution=resolutionG1, margin=margin,
                    align=tkl.BBOX_ALIGN_LL,
                    novalue=tkl.NO_DATA_VALUE)

    uidMap = rasterG1.addAFMap("uid")
    uidMap.addCountDistinct()


    # =========================================================================
    #      On construit G2
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ('    Building low-resolution contextual density grid G2 : ', G2_SIZE, 'm ...')

    resolutionG2 = (G1_SIZE, G1_SIZE)

    rasterG2 = tkl.Raster(bbox=bbox, resolution=resolutionG2, margin=margin,
                    align=tkl.BBOX_ALIGN_LL,
                    novalue=tkl.NO_DATA_VALUE)

    uidMap = rasterG2.addAFMap("uid")
    uidMap.addCountDistinct()


    # =========================================================================
    #      On alimente les deux grilles avec les traces
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ('    Assigning track points to the G1 and G2 grids')

    cpt = 1
    tracks = tkl.TrackSource(resampledtracespath, fmt)
    for track in tracks:

        if cpt%1000 == 0 and (log_level == 'INFO' or log_level == 'DEBUG'):
            print ('        ', cpt, '/', total)
        cpt += 1

        tid = track.getObsAnalyticalFeature('TID', 0)
        mid = track.getObsAnalyticalFeature('MID', 0)
        track.uid = tid
        track.tid = mid

        rasterG1.accumulate(tkl.TrackCollection([track]))
        rasterG2.accumulate(tkl.TrackCollection([track]))


    # =========================================================================
    #       Calcul des densités des traces GPS

    # compute aggregate
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ("    Computing G1 ...")
    rasterG1.compute()

    # Plus la densité
    uidmap = rasterG1.getAFMap("uid")
    bandG1 = uidmap["count_distinct"]
    bandG1.setGrid(bandG1.getGrid().values / (G1_SIZE*G1_SIZE))

    # -------------------------------------------------------------------------

    # compute aggregate
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ("    Computing G2 ...")
    createG2(rasterG2, G1_SIZE, G2_SIZE, log_level)


    # Plus la densité
    bandG2 = rasterG2.getAFMap("uid")["count_distinct"]
    #bandG2.setGrid(bandG2.getGrid().values / (G2_SIZE*G2_SIZE))


    # -------------------------------------------------------------------------
    # On enregistre les résultats
    pathG1 = respath + 'G1_' + prefix + '.asc'
    rasterG1.writeToAscFile(bandG1, pathG1)

    # On enregistre les résultats
    pathG2 = respath + 'G2_' + prefix + '.asc'
    rasterG2.writeToAscFile(bandG2, pathG2)


    # =============================================================================
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ('    Building contrast grid : ', G1_SIZE, 'm')

    epsilon = 0.001
    
    # On construit une grille vide comme G1 pou K
    box = tkl.Bbox(tkl.ENUCoords(rasterG1.xmin, rasterG1.ymin),
                   tkl.ENUCoords(rasterG1.xmax, rasterG1.ymax))
    res = rasterG1.resolution
    margin = 0
    align = tkl.BBOX_ALIGN_CENTER
    rasterK = tkl.Raster(bbox=box, resolution=res, margin=margin, align=align)
    mapK = rasterK.addAFMap('K')
    mapK.addValues()

    grilleG1 = bandG1.getGrid().values
    grilleG2 = bandG2.getGrid().values

    bandK = rasterK.getAFMap('K')['values']

    for i in range(rasterK.nrow):
        for j in range(rasterK.ncol):
            x = rasterK.xmin + j * res[0] + 1
            y = rasterK.ymin - (i - rasterK.nrow + 1) * res[1] + 1

            (column1, line1) = rasterG1.getCell(tkl.ENUCoords(x, y))
            g1 = grilleG1[line1][column1]

            (column2, line2) = rasterG2.getCell(tkl.ENUCoords(x, y))
            g2 = grilleG2[line2][column2]
    
            #g2 = G2[line][column] / (nb * G1_SIZE * nb * G1_SIZE)
            #g2 = grilleG2[line][column] / (G2_SIZE * G2_SIZE)
    
            if g1 <= 2 / (G1_SIZE * G1_SIZE):
                g1 = 0
    
            if g2 <= 0:
                g2 = epsilon
    
            k = g1 / g2
    
            bandK.getGrid().values[i][j] = k
    
    # bandK = rasterK.getAFMap('K')['values']
    
    pathK = respath + 'K_' + prefix + '.asc'
    rasterK.writeToAscFile(bandK, pathK)


    # =============================================================================

    # On construit une grille vide comme G1
    box = tkl.Bbox(tkl.ENUCoords(rasterK.xmin, rasterK.ymin),
                   tkl.ENUCoords(rasterK.xmax, rasterK.ymax))
    res = rasterK.resolution
    margin = 0
    align = tkl.BBOX_ALIGN_CENTER
    rasterB = tkl.Raster(bbox=box, resolution=res, margin=margin, align=align)
    mapB = rasterB.addAFMap('B')
    mapB.addValues()

    bandB = rasterB.getAFMap('B')['values']
    
    for i in range(rasterB.nrow):
        for j in range(rasterB.ncol):
            v = bandK.getGrid().values[i][j]
            if v >= SEUIL_DENSITE:
                bandB.getGrid().values[i][j] = 1
            else:
                bandB.getGrid().values[i][j] = 0
    
    pathB = respath + 'B_' + prefix + '.asc'
    rasterB.writeToAscFile(bandB, pathB)

    t1 = time.time()
    total = t1-t0
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ("    Execution time (seconds):", total)
        print ("    Finished heatmap computation.")
    t0 = t1

    # =========================================================================

    pathB             = respath + 'B_' + prefix + '.asc'
    pathdilatation    = respath + 'dilatation_' + prefix + '.tif'
    patherosion       = respath + 'erosion_' + prefix + '.tif'
    pathimageclean    = respath + 'imageclean_' + prefix + '.tif'

    surfpath          = respath + 'surface_' + prefix + '.shp'
    roadsurfpath      = respath + 'road_surface_' + prefix + '.shp'
    roadsurflissepath = respath + 'road_surface_lissee_' + prefix + '.shp'
    squelettepath     = RESPATH + 'network/squelette_' + prefix + '.shp'

    

    # =========================================================================
    #   On charge le binaire

    rasterB = tkl.RasterReader.readFromAscFile(pathB, af_name='B', separator="\t")
    mapBinaire = rasterB.getAFMap('B')


    # =========================================================================
    #   Dilatation + Erosion
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ("    Starting morphological closing image ...")
    mask = np.array([
                [0,1,0],
                [1,1,1],
                [0,1,0]])

    # Dilatation
    mapBinaire.filter(mask=mask, aggregation=np.max)
    tkl.RasterWriter.writeMapToAscFile(pathdilatation, rasterB, mapBinaire[0])

    # Erosion
    mapBinaire.filter(mask=np.array([[1]]), aggregation=lambda x : 1-x)     # Dual de la carte
    mapBinaire.filter(mask=mask, aggregation=np.max)                        # Dilatation
    mapBinaire.filter(mask=np.array([[1]]), aggregation=lambda x : 1-x)     # Dual de la carte

    tkl.RasterWriter.writeMapToAscFile(patherosion, rasterB, mapBinaire[0])


    # Nettoyage : remplissage des trous et suppression des toutes petites zones
    asize = G1_SIZE * G1_SIZE * G1_SIZE * G1_SIZE + 1

    clean = remove_small_holes(mapBinaire[0].getGrid().values.astype(bool), area_threshold=asize,
                                     connectivity=1)
    clean = remove_small_objects(clean, min_size=asize,
                                     connectivity=1)
    clean_uint8 = clean.astype(np.uint8)
    mapBinaire[0].setGrid(clean_uint8)

    # print(np.unique(clean_uint8))
    tkl.RasterWriter.writeMapToAscFile(pathimageclean, rasterB, mapBinaire[0])

    t1 = time.time()
    total = t1-t0
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ("    Execution time (seconds):", total)
        print ("    Finished morphological opening.")
    t0 = t1



    # =========================================================================
    #   Vectorisation dans le layer surface

    if log_level == 'INFO' or log_level == 'DEBUG':
        print ("    Vectorizing cleaned image ...")

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
    dsDepart = gdal.Open(pathimageclean)
    srcband = dsDepart.GetRasterBand(1)

    gdal.Polygonize(srcband, None, layerSurface, dst_field, [], callback=None)

    # forcer écriture
    layerSurface.SyncToDisk()
    dsSurface.FlushCache()
    
    # fermeture propre
    layerSurface = None
    dsSurface = None
    dsDepart = None


    # =========================================================================
    # On "extrait" les roads vers RoadSurface

    if log_level == 'INFO' or log_level == 'DEBUG':
        print ("    Extracting road surface vector features ...")

    NB_GS = 0
    NB_PS = 0
    MOY_PS = 0

    # ouvrir la source
    dsSurface = ogr.Open(surfpath)
    layer = dsSurface.GetLayer(0)
    NB_TOT = layer.GetFeatureCount()
    if log_level == 'INFO' or log_level == 'DEBUG':
        print("        Number of polygonize features: ", NB_TOT)

    dsRoadSurface = shpDriver.CreateDataSource(roadsurfpath)
    layerRoadSurface = dsRoadSurface.CreateLayer("road_surface", srs=l93Ref)

    
    # DN=0 + filtre sur la surface + id + enleve le cadre
    #       on corrige la géométrie
    

    field_defn = ogr.FieldDefn("id", ogr.OFTInteger)
    layerRoadSurface.CreateField(field_defn)

    cpt = 0

    minx1, maxx1, miny1, maxy1 = layerRoadSurface.GetExtent()
    extent = bbox_to_polygon(minx1, maxx1, miny1, maxy1)

    for feat in layer:
        geom = feat.GetGeometryRef()
        # print(geom.IsValid(), feat.GetField("DN"))

        if feat.GetField("DN") == 1:
            # print ('DN = 1')
            if geom is not None:
                area = geom.GetArea()
                if area > SEUIL_SURFACE:
                    # print ('Bonne surface')

                    minx2, maxx2, miny2, maxy2 = geom.GetEnvelope()
                    envelope = bbox_to_polygon(minx2, maxx2, miny2, maxy2)

                    intersection = extent.Intersection(envelope)
                    union = extent.Union(envelope)
                    iou = intersection.GetArea() / union.GetArea()
                    if iou < 0.99:
                        cpt += 1

                        width = maxx2 - minx2
                        height = maxy2 - miny2
                        elongation = max(width, height) / min(width, height)
                        if elongation < 5 and geom.GetArea() < 250:
                            # on s'approche d'un carré
                            if log_level == 'DEBUG':
                                print ('    Small geometry is approximately square.')
                            continue

                        # print ('pas cadre')
                        g = geom.Clone()
                        if not g.IsValid():
                            g = g.Buffer(0)

                        new_feat = ogr.Feature(layerRoadSurface.GetLayerDefn())
                        new_feat.SetGeometry(g)
                        new_feat.SetField("id", cpt)
                        layerRoadSurface.CreateFeature(new_feat)
                        NB_GS += 1
                        new_feat = None

                else:
                    NB_PS += 1
                    MOY_PS += area


    if log_level == 'INFO' or log_level == 'DEBUG':
        print("            Number of polygonize features copied: ", cpt)

    # fermer proprement
    layerRoadSurface.SyncToDisk()
    dsRoadSurface = None







    # -----------------------------------------
    #
    t1 = time.time()
    total = t1-t0
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ("    Execution time (seconds):", total)
        print ("    Vectorization completed.")
    t0 = t1



    # =========================================================================
    #   Lissage du polygone pour oublier le profil en escalier

    if log_level == 'INFO' or log_level == 'DEBUG':
        print ('    Smoothing polygon to remove stair-step artifacts ...')

    smoothingLayer(roadsurfpath, roadsurflissepath, shpDriver, G1_SIZE, cut_factor)

    t1 = time.time()
    total = t1-t0
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ("    Execution time (seconds):", total)
        print ("    Road surface smoothing completed.")
    t0 = t1


    # =========================================================================
    #   Squeletisation : centerline
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ('    Starting centerline computation ...')

    Shp2centerline(roadsurflissepath, squelettepath, interp_dist, clean_dist, verbose=verbose)

    t1 = time.time()
    total = t1-t0
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ("    Execution time (seconds):", total)
        print ("    Centerline computed.")


    # =========================================================================
    #    Journalisation des résultats

    n_features = 0
    with fiona.open(squelettepath, 'r') as shapefile:
        n_features = len(shapefile)

    try:
        if NB_PS == 0:
            moy = 0
        else:
            moy = round(MOY_PS / NB_PS)
        log_event(RESPATH + "image"+ str(prefix) + ".json", {
            "High-resolution grid cell size (m)": G1_SIZE,
            "Low-resolution grid cell size (m)": G2_SIZE,
            "Number of neighboring cells to consider": math.floor(G2_SIZE / (G1_SIZE*2)),
            "Cell cluster size threshold for filling or removal (m2)": asize,
            "Number of polygonize features": NB_TOT,
            "Number of small polygonized features": NB_PS,
            "Average area of small polygons (m2)": moy,
            "Number of polygonized features above threshold": NB_GS,
            "Number of edges in the skeleton": n_features,
            "ts": time.time()
        })
    except Exception as e:
        print (e)
        print ('Error while writing image information to log')


    # =========================================================================

    print ("Stage 2 completed: rasterization and vectorization.")
    # Fin



def createG2(rasterG2, G1_SIZE, G2_SIZE, log_level = 'ERROR'):
    grid = []
    for i in range(rasterG2.nrow):
        grid.append(i)
        grid[i] = []
        for j in range(rasterG2.ncol):
            grid[i].append(j)
            grid[i][j] = []


    #for cell, ids in self._cells.items():
    #    self._grid2d.values[cell[0]][cell[1]] = len(ids)
    #rasterG2.getAFMap('uid')['count_distinct'].finalize()
    #for (i, j), tarray in rasterG2.collectionValuesGrid['uid'].items():
    #    for s in tarray:
    #        grid[i][j].append(s)


    grilleG2 = rasterG2.getAFMap('uid')
    nb = math.floor(G2_SIZE / (G1_SIZE*2))
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ('    Number of neighboring cells to consider:', nb)

    bandCountDistinct = grilleG2['count_distinct']
    for i in range(rasterG2.nrow):
        for j in range(rasterG2.ncol):
            unique_values = set()
            for s in range(max(0,i-nb), min(i+nb+1, rasterG2.nrow)):
                for t in range(max(0,j-nb), min(j+nb+1, rasterG2.ncol)):
                    # all_values = grid[s][t]
                    tab = bandCountDistinct.getCellUniqueValue()
                    all_values = tab[(s, t)]
                    for st in all_values:
                        unique_values.add(st)
            grilleG2["count_distinct"].getGrid().values[i][j] = len(unique_values)

    # Plus la densité
    bandG2 = rasterG2.getAFMap("uid")["count_distinct"]
    bandG2.setGrid(bandG2.getGrid().values / (G2_SIZE*G2_SIZE))


def bbox_to_polygon(minx, maxx, miny, maxy):
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(minx, miny)
    ring.AddPoint(maxx, miny)
    ring.AddPoint(maxx, maxy)
    ring.AddPoint(minx, maxy)
    ring.AddPoint(minx, miny)

    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    return poly



def smoothingLayer(roadsurfpath, roadsurflissepath, shpDriver, r, f):

    dsRoadSurface = ogr.Open(roadsurfpath, 1)
    layerRoadSurface = dsRoadSurface.GetLayer()

    # Créer datasource
    dsRoadSurfaceLissee = shpDriver.CreateDataSource(roadsurflissepath)
    
    # Créer layer
    layerRoadSurfaceLissee = dsRoadSurfaceLissee.CreateLayer(
        "road_surface_lissee",
        layerRoadSurface.GetSpatialRef(),
        geom_type = ogr.wkbPolygon
    )
    
    # copier les champs attributaires
    src_defn = layerRoadSurface.GetLayerDefn()
    for i in range(src_defn.GetFieldCount()):
        field_defn = src_defn.GetFieldDefn(i)
        layerRoadSurfaceLissee.CreateField(field_defn)

    dst_defn = layerRoadSurfaceLissee.GetLayerDefn()


    dsRoadSurface = ogr.Open(roadsurfpath, 0)
    layerRoadSurface = dsRoadSurface.GetLayer()
    for feature in layerRoadSurface:
        geom = feature.GetGeometryRef().Clone()
        if geom is None:
            continue

        polygon = ogr.Geometry(ogr.wkbPolygon)

        # ==================================================================
        # Gestion de l'extérieur
        # ==================================================================
        exterior_ring = geom.GetGeometryRef(0)
        exterior = exterior_ring.GetPoints()
        # x = [p[0] for p in exterior]
        # y = [p[1] for p in exterior]
        # plt.plot(x, y, 'b-', linewidth=0.5)

        # ------------------------------------------------------------------
        # Géométrie filtrée
        # ------------------------------------------------------------------
        out = smoothing(exterior, r, f)
        xout = [p[0] for p in out]
        yout = [p[1] for p in out]
        #plt.plot(xout, yout, 'r-', linewidth=0.75)

        # ------------------------------------------------------------------
        # Construit une ligne
        # ------------------------------------------------------------------
        newring = ogr.Geometry(ogr.wkbLinearRing)
        for i in range(len(xout)):
            newring.AddPoint(xout[i], yout[i])
        newring.CloseRings()
        polygon.AddGeometry(newring)

        # ==================================================================
        # Gestion des intérieurs éventuels
        # ==================================================================
        for j in range(1, geom.GetGeometryCount()):
            ring = geom.GetGeometryRef(j)
            interior = ring.GetPoints()
            is_closed = interior[0] == interior[-1]
            if not is_closed or geom.GetArea() <= 0.001:
                continue

            #x = [p[0] for p in interior]
            #y = [p[1] for p in interior]
            #plt.plot(x, y, 'b-', linewidth=0.5)
                
            # ------------------------------------------------------------------
            # Géométrie filtrée
            # ------------------------------------------------------------------
            out = smoothing(interior, r, f)
            xout = [p[0] for p in out]
            yout = [p[1] for p in out]
            #plt.plot(xout, yout, 'r-', linewidth=0.75)

            # ------------------------------------------------------------------
            # Construit une ligne
            # ------------------------------------------------------------------
            newring = ogr.Geometry(ogr.wkbLinearRing)
            for i in range(len(xout)):
                newring.AddPoint(xout[i], yout[i])
            newring.CloseRings()
            polygon.AddGeometry(newring)


        # =====================================================================
        # Créer une nouvelle feature
        # =====================================================================
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
    




# --------------------------------------------------------------------------------------
# Filtre de Fourier coupe-bande sur une géométrie
# --------------------------------------------------------------------------------------
# Inputs:
#    - geom  : polygone (simple)
#    - r     : résolution centrale de coupure (en m)
#    - f     : facteur de coupure
# Output: géométrie filtrée avec suppression de toutes les longueurs d'onde comprises 
# entre r/f et r*f
# --------------------------------------------------------------------------------------
def smoothing(geom, r, f):

    # Préparation
    wl_sup = r*f
    wl_inf = r/f
    
    x = [p[0] for p in geom]
    y = [p[1] for p in geom]
    
    trace = tkl.Track()
    for ii in range(len(x)):
        trace.addObs(tkl.Obs(tkl.ENUCoords(x[ii], y[ii], 0)))

    N = len(trace)
    
    # Centrage du signal
    trace = trace.copy()
    c0 = trace.getCentroid(); 
    cx = c0.E; cy = c0.N
    trace.translate(-cx, -cy)
    
    # Sauvegarde des extrémités
    ci = trace[0]
    cf = trace[-1]
    
    # Periodisation du signal
    geom_in = trace + trace + trace
    
    # Filtre coupe-bande
    signal_low_freq = tkl.filter_freq(geom_in, (1.0/wl_sup), mode=tkl.FILTER_SPATIAL,
                                      type=tkl.FILTER_LOW_PASS , dim=tkl.FILTER_XY)[N:2*N]
    signal_hgh_freq = tkl.filter_freq(geom_in, (1.0/wl_inf), mode=tkl.FILTER_SPATIAL,
                                      type=tkl.FILTER_HIGH_PASS, dim=tkl.FILTER_XY)[N:2*N]
   
    # Somme passe-haut/passe-bas
    out = trace.copy()
    for i in range(N):
        out[i, "x"] = signal_low_freq[i, "x"] + signal_hgh_freq[i, "x"]
        out[i, "y"] = signal_low_freq[i, "y"] + signal_hgh_freq[i, "y"] 
        
    # Reconstruction des extrémités 
    out[0]  = ci
    out[-1] = cf   
        
    # Decentrage du signal
    out.translate(cx, cy)
    
    # Retransformation en géométrie
    out_geom = [(obs.position.getX(), obs.position.getY()) for obs in out]
    
    return out_geom





