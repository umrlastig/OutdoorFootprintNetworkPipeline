# -*- coding: utf-8 -*-

'''
Refinement phase


'''


# Trouver les points des traces qui ne sont pas appariées
#    + trouver les points qui n'ont pas servi
# On les prend si ce sont des bonnes traces


import math
import os
import sys
import csv
csv.field_size_limit(sys.maxsize)

import tracklib as tkl

import fiona
from shapely.geometry import shape
import progressbar
from scipy.ndimage import maximum_filter
import numpy as np
from osgeo import gdal, ogr, osr

from pipeline import Shp2centerline
from pipeline import createNetwork, filtreNoeudSimple, deleteSmallEdge
from pipeline import removeDuplicateGeometries
from pipeline import skeleton_smoothing



def second_round(RESPATH, NB_OBS_MIN, G1_SIZE, G2_SIZE, SEUIL, SEUIL_SURFACE, DIST_MIN_ARC,
                 RESAMPLE_SIZE_GRID):

    buffer_size = 5
    k = 0.6

    OPT_PLUS_PTS = True
    NB_PTS = 4


    # =========================================================================
    #   Lecture des traces découpées et ré-échantillonnées.
    #

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
    print ('Number of tracks map matched :', collection.size())

    index =  tkl.SpatialIndex(collection)

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
                # POINTS = index.neighborhood(obs.position, None, buffer_size)
                # TODO : il faudrait trouver le barycentre et faire le kième de la distance encore
                # print (len(POINTS))

                morceau.addObs(obs.copy())

            else:
                if cptNot >= NB_OBS_MIN:
                    if OPT_PLUS_PTS:
                        morceau = track.extract(j-NB_PTS, j) + morceau
                        if j < track.size()-1:
                            morceau = morceau + track.extract(j+1, min(j+NB_PTS, track.size()-1))
                    morceau.resample(RESAMPLE_SIZE_GRID, mode=tkl.MODE_SPATIAL)
                    morceaux.addTrack(morceau)

                morceau = tkl.Track()
                morceau.tid = cpt
                morceau.uid = cpt
                cpt += 1
                cptNot = 0

        if cptNot >= NB_OBS_MIN:
            if OPT_PLUS_PTS:
                morceau = track.extract(j-NB_PTS, j) + morceau
                if j < track.size()-1:
                    morceau = morceau + track.extract(j+1, min(j+NB_PTS, track.size()-1))
            morceau.resample(RESAMPLE_SIZE_GRID, mode=tkl.MODE_SPATIAL)
            morceaux.addTrack(morceau)


    # On enregistre
    # print (morceaux.size())

    tracespath = RESPATH + "points_not_mm/"
    tkl.TrackWriter.writeToFiles(morceaux, tracespath,
                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                 h=1, separator=";") # af_names=af_names



    '''
    
       


    # =============================================================================
    #          CHARGEMENT DU SQUELETTE

    tolerance     = 0.1    # 0.05
    seuil_doublon = 0.1

    collection = tkl.TrackCollection()

    with fiona.open(squelettepath, 'r') as shapefile:
        for feature in shapefile:
            # 1 MultiLineString
            geom = shape(feature['geometry'])
            if geom.geom_type == "MultiLineString":
                for line in geom.geoms:
                    track = tkl.TrackReader().parseWkt(line.wkt)
                    if track.length() < tolerance/2:
                        continue
                    collection.addTrack(track)

    print ('Nb lignes : ', collection.size())



    # =============================================================================
    #             CONSTRUCTION RESEAU
    #
    # Pour la construction du réseau


    tkl.NetworkReader.counter = 1
    
    network = createNetwork(collection, tolerance)


    network.simplify(0, tkl.MODE_SIMPLIFY_REM_POS_DUP, verbose=False)

    filtreNoeudSimple(network)


    cpt = 0
    nb = 1000
    while nb > 10 and cpt < 10:
        nb = deleteSmallEdge(network, DIST_MIN_ARC)
        print ('    nb arcs supprimés: ', nb)
        cpt += 1
    filtreNoeudSimple(network)


    cpt = 0
    nb = 1000
    while nb > 10 and cpt < 10:
        nb = deleteSmallEdge(network, DIST_MIN_ARC)
        print ('    nb arcs supprimés: ', nb)
        cpt += 1
    filtreNoeudSimple(network)


    print ('Fin suppression des petis arcs 4/4.')



    network.simplify(0, tkl.MODE_SIMPLIFY_REM_POS_DUP, verbose=False)
    network.simplify(5, tkl.MODE_SIMPLIFY_DOUGLAS_PEUCKER, verbose=False)



    # Sauvegarde dans un fichier
    netwokpath = RESPATH + 'network/reseau_ST.csv'
    tkl.NetworkWriter.writeToCsv(network, netwokpath)

    '''