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
import time
from scipy.ndimage import maximum_filter

import matplotlib.pyplot as plt

import tracklib as tkl
import numpy as np

from osgeo import gdal, ogr, osr
from pipeline import Shp2centerline





def density_polygonize(RESPATH, G1_SIZE, G2_SIZE, SEUIL_DENSITE, SEUIL_SURFACE, prefix='PT',
                       rep='resample_grid', f=2):

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
    t0 = time.time()

    fmt = tkl.TrackFormat({'ext': 'CSV',
                           'srid': 'ENU',
                           'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                           'separator': ';',
                           'header': 1,
                           'read_all': True})
    
    resampledtracespath = RESPATH + rep + '/'

    bbox = tkl.Bbox(tkl.ENUCoords(947991.025, 6510752.689),
                    tkl.ENUCoords(951187.721, 6513143.062))

    af_algos = ['uid']
    cell_operators = [tkl.co_count_distinct]

    marge = 0
    resolutionG1 = (G1_SIZE, G1_SIZE)

    rasterG1 = tkl.Raster(bbox=bbox, resolution=resolutionG1, margin=marge,
                    align=tkl.BBOX_ALIGN_LL,
                    novalue=tkl.NO_DATA_VALUE)


    # Pour chaque algo-agg on crée une grille vide
    for idx, af_algo in enumerate(af_algos):
        aggregate = cell_operators[idx]
        cle = tkl.AFMap.getMeasureName(af_algo, aggregate)
        rasterG1.addAFMap(cle)



    tracks = tkl.TrackSource(resampledtracespath, fmt)
    total = len(tracks)
    print ('Number files to load: ', total)

    # collection = tkl.TrackCollection()
    # tkl.TrackReader.readFromFile(resampledtracespath, fmt)


    cpt = 1
    for trace in tracks:

        if cpt%500 == 0:
            print ('    ', cpt, '/', total)
        cpt += 1

        trace.uid = trace.getObsAnalyticalFeature('user_id', 0)
        trace.tid = trace.getObsAnalyticalFeature('track_id', 0)

        rasterG1.addCollectionToRaster(tkl.TrackCollection([trace]))






    # =============================================================================
    #       Calcul des densités des traces GPS


    # compute aggregate
    print ("Starting to compute aggregates ...")
    rasterG1.computeAggregates()

    
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
            if v > SEUIL_DENSITE:
                raster.getAFMap(0).grid[i][j] = 1
            else:
                raster.getAFMap(0).grid[i][j] = 0
    
    pathB = respath + 'B_' + prefix + '.asc'
    tkl.RasterWriter.writeMapToAscFile(pathB, raster.getAFMap(0))


    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)
    print ("Fin des calculs des cartes de densités, de constraste et binaire.")
    t0 = t1

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
    if prefix=='PT':
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
    else:
        pathdepart = pathdilatation


    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)
    print ("Fin de l'ouverture.")
    t0 = t1

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
    #   Squeletisation : DN=0 + filtre sur la surface + id + enleve le cadre
    #       on corrige la géométrie

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
    #    On enlève les polygones trop petit
    fids_to_delete = []

    for feature in layerRoadSurface:
        geom = feature.GetGeometryRef()
        if geom is not None:
            area = geom.GetArea()
            if area <= SEUIL_SURFACE:
                fids_to_delete.append(feature.GetFID())
            # else:
            #    print ("Un polygone gardé avec comme surface", area, SEUIL_SURFACE)

    for fid in fids_to_delete:
        layerRoadSurface.DeleteFeature(fid)




    # ------------------------------------------
    #   On enlève le cadre

    fids_to_delete = []

    minx1, maxx1, miny1, maxy1 = layerRoadSurface.GetExtent()
    extent = bbox_to_polygon(minx1, maxx1, miny1, maxy1)
    for feature in layerRoadSurface:
        geom = feature.GetGeometryRef()
        if geom is not None:
            minx2, maxx2, miny2, maxy2 = geom.GetEnvelope()
            envelope = bbox_to_polygon(minx2, maxx2, miny2, maxy2)

            intersection = extent.Intersection(envelope)
            union = extent.Union(envelope)
            iou = intersection.GetArea() / union.GetArea()
            if iou >= 0.99:
                fids_to_delete.append(feature.GetFID())

    for fid in fids_to_delete:
        layerRoadSurface.DeleteFeature(fid)



    # -----------------------------------------
    #   On ajoute une colonne Id (je ne sais plus pourquoi)

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


    # -----------------------------------------
    #   On essaie de corriger les géométries

    for feature in layerRoadSurface:
        geom = feature.GetGeometryRef()
        geom = geom.Buffer(0)

    dsRoadSurface = None



    # -----------------------------------------
    #
    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)
    print ("Fin de la vectorisation.")
    t0 = t1




    # =========================================================================
    #   Lissage du polygone pour oublier le profil en escalier

    # filtre(roadsurfpath, roadsurflissepath, shpDriver)
    # dual(roadsurfpath, roadsurflissepath, shpDriver)
    filtre (roadsurfpath, roadsurflissepath, shpDriver, G1_SIZE, f)


    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)
    print ("Fin du lissage de road surface.")
    t0 = t1


    # =========================================================================
    #   Squeletisation : centerline

    interp_dist = 5
    clean_dist  = 0

    Shp2centerline(roadsurflissepath, squelettepath, interp_dist, clean_dist)
    
    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)
    print ("Fin du calcul de la center line.")

    # =========================================================================


    print ("Fin des calculs de vectorisation et squelette.")



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



def filtre(roadsurfpath, roadsurflissepath, shpDriver, r, f):

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
        x = [p[0] for p in exterior]
        y = [p[1] for p in exterior]
        plt.plot(x, y, 'b-', linewidth=0.5)

        # ------------------------------------------------------------------
        # Géométrie filtrée
        # ------------------------------------------------------------------
        out = smoothing(exterior, r, f)
        xout = [p[0] for p in out]
        yout = [p[1] for p in out]
        plt.plot(xout, yout, 'r-', linewidth=0.75)

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
            print ('une géométrie intérieure')

            x = [p[0] for p in interior]
            y = [p[1] for p in interior]
            plt.plot(x, y, 'b-', linewidth=0.5)
                
            # ------------------------------------------------------------------
            # Géométrie filtrée
            # ------------------------------------------------------------------
            out = smoothing(interior, r, f)
            xout = [p[0] for p in out]
            yout = [p[1] for p in out]
            plt.plot(xout, yout, 'r-', linewidth=0.75)

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


'''
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

'''
