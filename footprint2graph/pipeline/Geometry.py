# -*- coding: utf-8 -*-

'''
    Recalage des points sur le réseau
    Fusion des traces
'''


import sys
import csv
csv.field_size_limit(sys.maxsize)
import time

import tracklib as tkl

from footprint2graph import conflateOnNetwork
from footprint2graph import prepareMapMatchResultForCreateCandidates
from footprint2graph import getcandidates
from footprint2graph import aggregate_track_segments_by_edge



def createNetworkGeom (RESPATH, SEARCH, BUFFER, pipeline_idx = None):


    t0 = time.time()
    print("Starting map-matching, aggregation, and conflation of GNSS trajectories.")

    idx = int (pipeline_idx)
    prefix = str(idx)

    if idx == 1:
        pathtraces = 'resample_fusion'
    else:
        pathtraces = 'points_not_mm_' + prefix

    pathtmm = 'tmm' + prefix
    pathraccord = 'raccord' + prefix




    # =========================================================================
    #    Lecture du réseau
    #
    print ('    Loading network (' + prefix + ') ...')
    fmt = tkl.NetworkFormat({
           "pos_edge_id": 0,
           "pos_source": 1,
           "pos_target": 2,
           "pos_wkt": 4,
           "srid": "ENU",
           "separator": ",",
           "header": 1})
    
    networkpath = RESPATH + 'network/reseau_' + prefix + '.csv'
    network = tkl.NetworkReader.readFromFile(networkpath, fmt, verbose=False)
    
    print ('        Number of edges = ', len(network.EDGES))
    print ('        Number of nodes = ', len(network.NODES))
    print ('        Total segment length of the network = ', network.totalLength())

    
    # =========================================================================
    #   Lecture des traces découpées et ré-échantillonnées.
    #
    print ('    Loading collection of tracks ...')
    fmt = tkl.TrackFormat({'ext': 'CSV',
                           'srid': 'ENU',
                           'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                           'time_fmt': '2D/2M/4Y 2h:2m:2s',
                           'separator': ';',
                           'header': 0,
                           'cmt': '#',
                           'read_all': True})
    tracespath = RESPATH + '/' + pathtraces + '/'
    try:
        collection2 = tkl.TrackReader.readFromFile(tracespath, fmt)
    except Exception as e:
        print (e)
        print (tracespath)

    collection = tkl.TrackCollection()
    for trace in collection2:
        num = trace.getObsAnalyticalFeature('TID', 0)
        numofnp = trace.getObsAnalyticalFeature('MID', 0)
        trace.uid = num
        trace.tid = numofnp
        collection.addTrack(trace)


    print ('        Number of tracks:', collection2.size())

    t1 = time.time()
    total = t1-t0
    print ("        Execution time (seconds):", total)
    t0 = t1


    # =========================================================================
    #     Map-matching
    #
    print ('    Starting map-matching ...')

    si = tkl.SpatialIndex(network, verbose=False)
    print ('        Index spatial : ', si)
    network.spatial_index = si

    # Computes all distances between pairs of nodes
    network.prepare(verbose=False)

    # Map track on network
    print ('        Parameter search_radius: ', SEARCH)
    tkl.mapOnNetwork(collection, network, search_radius=SEARCH, debug=False, verbose=False)
    print ('        Map-matching ended.')

    t1 = time.time()
    total = t1-t0
    print ("        Execution time (seconds):", total)
    t0 = t1


    # =========================================================================
    #     1. Prepare map-matching results for candidate segment generation
    #
    print ('        Prepare map-matching results for candidate segment generation')

    NB_PTS = 5
    MM = prepareMapMatchResultForCreateCandidates(collection, network, SEARCH, NB_PTS, RESPATH, prefix)


    # Export map-matching results
    if RESPATH is not None:
        af_names = ['TID', 'MID', 'hmm_inference', 'mmtype', 'idedge', 'obs_noise', 'hmm_cost']
        mmtracespath = RESPATH + 'mapmatch/' + pathtmm + '/'
        tkl.TrackWriter.writeToFiles(collection, mmtracespath,
                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                 h=1, separator=";", af_names=af_names)
        print ('        Map-matching results exported.')


    # 2. Résultats Map-matching
    #
    getcandidates(MM, network, collection, BUFFER, RESPATH, prefix)
    t1 = time.time()
    total = t1-t0
    print ("        Execution time (seconds):", total)
    t0 = t1



    # =========================================================================
    #     Fusion
    #
    fusions = aggregate_track_segments_by_edge(network, SEARCH, RESPATH, prefix)

    t1 = time.time()
    total = t1-t0
    print ("        Execution time (seconds):", total)
    t0 = t1


    # =========================================================================
    # Raccord

    print ("    Starting conflation ...")

    threshold = 20 # 50
    h = 20
    conflated = conflateOnNetwork(fusions, network,
                                  threshold, h,
                                  RESPATH,
                                  prefix,
                                  verbose=False)

    # enregistrer conflation
    raccordpath = RESPATH + 'geometry/' + pathraccord + '/'
    for segment in conflated:
        if segment is not None:
            # Sauvegarde
            chemin = raccordpath + str(segment.tid) + ".csv"
            f = open(chemin, 'w')
            f.write("EDGE_ID;WKT\n")
            f.write(str(segment.tid) + ";" + segment.toWKT() + "\n")
            f.close()

    print ("        Conflation process finished.")

    t1 = time.time()
    total = t1-t0
    print ("        Execution time (seconds):", total)
    t0 = t1


    # =========================================================================
    # Fin
    
    print ("Stage 4 completed: map-matching, aggregation, and conflation.")

    






