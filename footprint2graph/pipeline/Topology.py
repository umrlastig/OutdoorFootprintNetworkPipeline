# -*- coding: utf-8 -*-

'''
      TOPOLOGIE DU SQUELETTE
'''


import fiona
from shapely.geometry import shape
import os
import progressbar
import time
import matplotlib.pyplot as plt
import sys

import tracklib as tkl

from footprint2graph import skeleton_smoothing, conflateTurnOnTerminalEdge, snap_lines_to_connect
from footprint2graph import log_event


def addTopologyToNetwork(RESPATH, SEARCH, h=10,
                         NB_OBS_MIN = 10, RESAMPLE_SIZE_FUSION = 5,
                         pipeline_idx = None, log_level='ERROR'):

    t0 = time.time()
    print("Starting topology creation for the network")

    idx = int (pipeline_idx)
    prefix = str(idx)

    # Pour la construction du réseau
    tolerance     = 0.1    # 0.05

    squelettepath = str(RESPATH) + 'network/squelette_' + str(idx) + '.shp'

    if log_level == 'ERROR':
        verbose = False
    else:
        verbose = True


    # =========================================================================
    #          CHARGEMENT DU SQUELETTE

    collection = tkl.TrackCollection()
    cptTrack = 1
    with fiona.open(squelettepath, 'r') as shapefile:
        for feature in shapefile:
            # 1 MultiLineString
            geom = shape(feature['geometry'])
            if geom.geom_type == "MultiLineString":
                for line in geom.geoms:
                    track = tkl.TrackReader().parseWkt(line.wkt)
                    if track.length() < tolerance/2:
                        continue
                    track.tid = cptTrack
                    cptTrack += 1
                    collection.addTrack(track)
            elif geom.geom_type == "LineString":
                # print (geom.geom_type)
                track = tkl.TrackReader().parseWkt(geom.wkt)
                if track.length() < tolerance/2:
                    continue
                track.tid = cptTrack
                cptTrack += 1
                collection.addTrack(track)
            else:
                if log_level == 'DEBUG':
                    print (geom.geom_type)


    NB_EDGES = collection.size()
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ('    Number of edges in the skeleton:', collection.size())
        print ('    Finished loaded skeleton.')

    if collection.size() == 0:
        sys.exit("Fin du programme le squelette est vide.")


    # =========================================================================
    #          Création d'un réseau surtout pour la fusion des arcs
    #

    input_file = str(RESPATH) + 'network/tmp_in.csv'
    output_file = str(RESPATH) + 'network/tmp_out.csv'
    try:
        os.remove(input_file)
    except FileNotFoundError:
        print ('    ' + input_file + " not exists")
    try:
        os.remove(output_file)
    except FileNotFoundError:
        print ('    ' + output_file + " not exists")


    with open(input_file, "w") as f:
        for track in collection:
            f.write(track.toWKT() + ";" + str(track.tid) + "\n")


    tkl.Topology.create_topology(input_file, '2154', output_file)
    fmt = tkl.NetworkFormat({
           "pos_edge_id": 0,
           "pos_source": 1,
           "pos_target": 2,
           "pos_wkt": 3,
           "srid": "ENU",
           "separator": ",",
           "header": 1})
    network = tkl.NetworkReader.readFromFile(output_file, fmt, verbose=False)
    collection = tkl.TrackCollection()
    cptTrack = 1
    for edge in network:
        track = edge.geom.copy()
        track.tid = cptTrack
        cptTrack += 1
        collection.addTrack(track)
    network = None


    # =========================================================================
    #         Suppression des doublons
    #

    tolerance = 0
    for track in collection:
        track = tkl.simplify(track, tolerance, tkl.MODE_SIMPLIFY_REM_POS_DUP,
                             verbose=verbose)
    print ('')
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ('    Finished removing hooked parts of the skeleton.')


    # =========================================================================
    #          LISSAGE: SUPPRIME LES parties crochues du squelette
    #

    for track in progressbar.progressbar(collection):
        track = skeleton_smoothing(track, 3, 6)


    # =========================================================================
    #          SIMPLIFICATION
    #

    tolerance = 3
    for track in collection:
        track = tkl.simplify(track, tolerance, tkl.MODE_SIMPLIFY_DOUGLAS_PEUCKER,
                             verbose=verbose)
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ('    Finished simplification of the skeleton.')



    # =========================================================================
    #          SNAPPING
    #
    tolerance = 1
    NB_START = collection.size()
    collection = snap_lines_to_connect(collection, tolerance, log_level=log_level)
    NB_END = collection.size()
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ('    Number of edges in the skeleton (after snapping):', collection.size())
        print ('    Edge count difference after snapping : ', NB_END - NB_START)




    # =========================================================================
    #          Création de la topologie
    #

    input_file = str(RESPATH) + 'network/edgegeom_' + prefix + '.csv'
    with open(input_file, "w") as f:
        for track in collection:
            f.write(track.toWKT() + ";" + str(track.tid) + "\n")

    output_file = str(RESPATH) + 'network/squelette_topology_simplifie_' + prefix + '.csv'
    tkl.Topology.create_topology(input_file, '2154', output_file, tbp=0.001)

    fmt = tkl.NetworkFormat({
           "pos_edge_id": 0,
           "pos_source": 1,
           "pos_target": 2,
           "pos_wkt": 3,
           "srid": "ENU",
           "separator": ",",
           "header": 1})
    network = tkl.NetworkReader.readFromFile(output_file, fmt, verbose=False)
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ('    Number of edges in the simplified skeleton:', len(network.getIndexEdges()))
        print ('    Number of nodes:', len(network.getIndexNodes()))




    # =========================================================================
    #          Suppression des petits arcs ISOLES
    #
    long_min = NB_OBS_MIN * RESAMPLE_SIZE_FUSION
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ('     Shortest edges limit : ', long_min)

    CPT_LEN_TOO_SHORT = 0
    for edge in network:
        test1 = edge.geom.length() < long_min
        test2 = len(network.getIncidentEdges(edge.source.id)) <= 1
        test3 = len(network.getIncidentEdges(edge.target.id)) <= 1
        if test1 and test2 and test3:
            network.removeEdge(edge)
            # pas besoin de supprimer des noeuds puisque isolés
            CPT_LEN_TOO_SHORT += 1
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ('    Number of edges in the skeleton (after removing the shortest edges):', CPT_LEN_TOO_SHORT)


    TE = list(map(int, network.getIndexEdges()))
    tkl.NetworkReader.counter = max(TE) + 1



    # =========================================================================
    #          "Déformation des virages s'ils suivent un pattern
    #   sous forme d'un T à l'envers , dont la longeur du tronc pas trop longue
    #                                  et dont le noeud terminal est 'isolé'
    #   et les deux autres arcs de la base plus longues que le tronc

    cpt = 0
    HC = []
    while True and cpt <= len(network.NODES):
        cpt += 1

        # 1. trouver les noeuds de degré 3
        nodes_deg3 = [nid for nid in network.getIndexNodes() if network.degree(nid) == 3]
        nodes_deg3 = [x for x in nodes_deg3 if x not in HC]
        # print (len(nodes_deg3), "/", len(network.getIndexNodes()))

        if not nodes_deg3:
            break

        # 2. traiter un noeud
        nid = nodes_deg3[0]
        # print ('Noeud en cours :', nid)

        r = conflateTurnOnTerminalEdge(network, nid, SEARCH, h, log_level=log_level)
        if r is None:
            HC.append(nid)

    # network.simplify(0, tkl.MODE_SIMPLIFY_REM_POS_DUP)
    if log_level == 'INFO' or log_level == 'DEBUG':
        print ('    Edge count after conflation:', len(network.getIndexEdges()))


    # =========================================================================
    #          Sauvegarde dans un fichier
    #

    netwokpath = RESPATH + 'network/reseau_' + prefix + '.csv'
    tkl.NetworkWriter.writeToCsv(network, netwokpath)


    # =========================================================================
    #    Journalisation des résultats

    try:
        log_event(RESPATH + "topology"+ str(idx) + ".json", {
            "Number of edges in the skeleton": NB_EDGES,
            "Number of skeleton edges removed for being too short": CPT_LEN_TOO_SHORT,
            "Edge count difference after snapping": NB_END - NB_START,
            "ts": time.time()
        })
    except Exception as e:
        print (e)
        print ('Error while logging skeleton topology')



    print ("Stage 3 completed: adding topology to the skeleton.")











