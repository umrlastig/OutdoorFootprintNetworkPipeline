# -*- coding: utf-8 -*-

'''
    Recalage des points sur le réseau
    Fusion des traces
'''

from math import *
import sys
import csv
csv.field_size_limit(sys.maxsize)
import time

import tracklib as tkl
from footprint2graph import (conflateOnNetwork,
                  getcandidates,
                  log_event)



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
    pathfusion = 'fusion' + prefix
    pathraccord = 'raccord' + prefix




    # =========================================================================
    #    Lecture du réseau
    #
    print ('Loading network (' + prefix + ') ...')
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
    
    print ('    Number of edges = ', len(network.EDGES))
    print ('    Number of nodes = ', len(network.NODES))
    print ('    Total segment length of the network = ', network.totalLength())

    
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
    print ('    Number of tracks:', collection2.size())


    # =========================================================================

    collection = tkl.TrackCollection()
    for trace in collection2:
        num = trace.getObsAnalyticalFeature('TID', 0)
        #if str(int(num)) != '228':
        #    continue
        # print (str(int(num)))

        numofnp = trace.getObsAnalyticalFeature('MID', 0)
        trace.uid = num
        trace.tid = numofnp
        #if str(trace.tid) == '6732043.0-v1' or str(trace.tid) == '6732043.0-v1':
        #if num in ['OV_1073-v1', 'OV_1739-v1', 'OV_1730-v1', 'OV_140-v1',
        #           'OV_1166-v1', 'OV_1-v1', 'OV_1530-v1', 'OV_1411-v1',
        #           'OV_1012-v1', 'OV_1012-v2', 'OV_1012-v3']:
        collection.addTrack(trace)
    # print ('    Number of tracks:', collection.size())

    t1 = time.time()
    total = t1-t0
    print ("    Execution time (seconds):", total)
    t0 = t1


    # =========================================================================
    #     Map-matching
    #
    print ('Starting map-matching ...')

    si = tkl.SpatialIndex(network, verbose=False)
    network.spatial_index = si

    # Computes all distances between pairs of nodes
    network.prepare()

    # Map track on network
    print('    PARAMETER search_radius: ', SEARCH)
    tkl.mapOnNetwork(collection, network, search_radius=SEARCH, debug=False, verbose=False)
    print ('    Map-matching ended.')


    t1 = time.time()
    total = t1-t0
    print ("    Execution time (seconds):", total)
    t0 = t1


    # On construit un dictionnaire qui va contenir l'ensemble des points MM
    #    avec  leurs séquences afin de reconstuire des traces candidates
    #    pour la fusion:
    #        la trace doit être proche de la source de l'arc et
    #                           proche de la target de l'arc
    #        sans trou (index manquant)
    #        géométrie dans le même que celui de l'arc
    #

    MM = {}   #  [ide][pkid] : liste des observations

    nbpt = 0
    nbmm = 0
    nbhp = 0
    rmse_total = 0
    nbtj = 0
    maxd = 0

    NB_PTS = 5

    for i in range(collection.size()):
        track = collection.getTrack(i)
        nbtj += 1
        MSE = 0

        # print (track.getListAnalyticalFeatures())
        # print (track.getObsAnalyticalFeature('TID', 0))
        track.createAnalyticalFeature('mmtype', 'NOT')
        track.createAnalyticalFeature('idedge', -1)
        pkid = track.tid
        # print (pkid)

        #if track.size() != 309: # and track.size() != 309:
        #    continue


        for j in range(track.size()):
            nbpt += 1

            pb  = track[j].position
            ds = float(track["hmm_inference", j][2])
            dt = float(track["hmm_inference", j][3])
            idxedge = int(track["hmm_inference", j][1])

            if idxedge > -1:
                nbmm += 1
                xraw = track[j].position.getX()
                yraw = track[j].position.getY()
                xmm = track["hmm_inference", j][0].getX()
                ymm = track["hmm_inference", j][0].getY()
                ecartpos = sqrt((xraw-xmm)**2 + (yraw-ymm)**2)
                MSE += ecartpos**2
                if ecartpos > maxd:
                    maxd = ecartpos
            else:
                nbhp += 1

            # print (idxedge)

            edgeid = network.getEdgeId(idxedge)
            #if edgeid != '79':
            #    continue
            #print (edgeid)
            #print ('+++++', idxedge, ds, dt)
            e = network.EDGES[edgeid]

            if idxedge == -1:
                track.setObsAnalyticalFeature('mmtype', j, 'NOT')
                track.setObsAnalyticalFeature('idedge', j, -1)

                # On s'autorise à combler les petits trous avec des points non appariés
                # s'ils ont une distance à l'arc petite
                # Pour connaitre l'arc, il faut passer par les points précédents
                # et les points suivants

                # l'arc precedent
                idxp = -1
                for k in range(j-1, max(-1, j-NB_PTS-1), -1):
                    idxp = int(track["hmm_inference", k][1])
                    if idxp > -1:
                        break
                # l'arc suivant
                idxs = -1
                for k in range(j+1, min(track.size(), j+NB_PTS+1), 1):
                    idxs = int(track["hmm_inference", k][1])
                    if idxs > -1:
                        break

                # print (j, idxp, idxs)

                # if idxp == idxs or idxp == -1 or idxs == -1:
                # - Il faut que ce soit le même arc, donc dans ce cas il faut
                #   des points recalés avant et des points recalés après
                if idxp == idxs and idxp > -1 and idxs > -1:

                    edgeidsupp = network.getEdgeId(idxp)
                    esupp = network.EDGES[edgeidsupp]
                    # on calcule la projection sur l'arc des points avant-apres
                    distmin, xproj, yproj, iproj = tkl.proj_polyligne(
                        esupp.geom.getX(), esupp.geom.getY(), pb.getX(), pb.getY())
                    # print (distmin, SEARCH)
                    if distmin < SEARCH:
                        if edgeidsupp not in MM:
                            MM[edgeidsupp] = {}
                        if pkid not in MM[edgeidsupp].keys():
                            MM[edgeidsupp][pkid] = []
                        # print (j)
                        MM[edgeidsupp][pkid].append((j,pb))
                        # print ('-----', j, edgeidsupp, pkid)

            elif ds > 0.01 and dt > 0.01:
                if edgeid not in MM:
                    MM[edgeid] = {}
                if pkid not in MM[edgeid].keys():
                    MM[edgeid][pkid] = []
                # print ('-----', j, edgeid, pkid)
                MM[edgeid][pkid].append((j,pb))
                track.setObsAnalyticalFeature('mmtype', j, 'EDGE')
                track.setObsAnalyticalFeature('idedge', j, edgeid)
            elif abs(ds) < 0.01:
                idnode = e.source.id
                edgesid = network.getIncidentEdges(idnode)
                for eid in edgesid:
                    if eid not in MM:
                        MM[eid] = {}
                    if pkid not in MM[eid].keys():
                        MM[eid][pkid] = []
                    MM[eid][pkid].append((j,pb))
                track.setObsAnalyticalFeature('mmtype', j, 'SOURCE')
                track.setObsAnalyticalFeature('idedge', j, idnode)
            elif abs(dt) < 0.01:
                idnode = e.target.id
                edgesid = network.getIncidentEdges(idnode)
                for eid in edgesid:
                    if eid not in MM:
                        MM[eid] = {}
                    if pkid not in MM[eid].keys():
                        MM[eid][pkid] = []
                    MM[eid][pkid].append((j,pb))
                track.setObsAnalyticalFeature('mmtype', j, 'TARGET')
                track.setObsAnalyticalFeature('idedge', j, idnode)
            else:
                print ('????')

        MSE = sqrt(MSE / track.size())
        rmse_total += MSE**2

    if nbtj == 0:
        rmse_total = -1
    else:
        rmse_total = sqrt(rmse_total/nbtj)

    # print (MM['23'])

    if RESPATH is not None:
        af_names = ['TID', 'MID', 'hmm_inference', 'mmtype', 'idedge', 'obs_noise', 'hmm_cost']
        mmtracespath = RESPATH + 'mapmatch/' + pathtmm + '/'
        tkl.TrackWriter.writeToFiles(collection, mmtracespath,
                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                 h=1, separator=";", af_names=af_names)
        print ('    Map-matching results exported.')

        if nbpt == 0:
            percentMM = 0
            percentHP = 0
        else:
            percentMM = (nbmm / nbpt * 100)
            print ('    Number of map-matched points = ' + str(nbmm) + ' (' + str(round(percentMM, 2)) + ' %)')
            percentHP = (nbhp / nbpt * 100)
        print ('    Map-matching results restructuring completed.')

        log_event(RESPATH + "mapmatch" + prefix + ".json", {
            "Search radius (m)": SEARCH,
            "Number of map-matched points": nbmm,
            "Percentage of map-matched points (%)": str(round(percentMM, 2)),
            "Number of off-track points": nbhp,
            "Percentage of off_track points (%)": str(round(percentHP, 2)),
            "Root Mean Square Error (m)": round(rmse_total),
            "Maximal displacement (m)": maxd,
            "ts": time.time()
        })




    # =========================================================================
    #  Résultats Map-matching
    #
    getcandidates(MM, network, collection, BUFFER, RESPATH, prefix)
    t1 = time.time()
    total = t1-t0
    print ("    Execution time (seconds):", total)
    t0 = t1


    # =========================================================================
    #     Fusion
    #

    print ("Starting aggregation ...")
    NBAP30 = 0
    NBAM30 = 0
    MIN    = 100000
    MOY    = 0

    geompath = RESPATH + 'geometry/' + pathfusion + '/'
    
    # Aggregation with DTW distance
    fusions = tkl.TrackCollection()
    edgeprevious = -1
    TRACES = []
    mmpath = RESPATH + 'mapmatch/resultmm_' + prefix + '.csv'
    with open(mmpath, 'r') as file:
        cpt = 0
        for s in file:

            if cpt == 0:
                cpt += 1
                continue

            line = s.split(";")
            if len(line) < 1:
                continue

            #  "EDGE_ID; TID; MID; WKT
            edgeid = line[0]

            if edgeprevious != edgeid and edgeprevious != -1:

                e = network.EDGES[edgeprevious]

                if e.geom.length() <= SEARCH:
                    print ("    No merge for arc number (length too small):", edgeprevious)
                    central = e.geom.copy()
                    central.createAnalyticalFeature('edgeid', edgeprevious)
                    central.tid = edgeprevious
                    fusions.addTrack(central)

                    # sauvegarde
                    chemin = geompath + str(edgeprevious) + ".csv"
                    f = open(chemin, 'w')
                    f.write("EDGE_ID;TRACKS_SIZE;WKT\n")
                    f.write(str(edgeprevious) + ";" + str(len(TRACES)) + ";" + central.toWKT() + "\n")
                    f.close()

                elif len(TRACES) >= 1:
                    print ("    Aggregation for arc number:", edgeprevious)
                    central = _fusion(e, TRACES, SEARCH)
                    MIN = min([MIN, len(TRACES)])
                    MOY += len(TRACES)
                    if len(TRACES) > 30:
                        NBAP30 += 1
                    else:
                        NBAM30 += 1
                    if central is not None:
                        central.createAnalyticalFeature('edgeid', edgeprevious)
                        central.tid = edgeprevious
                        fusions.addTrack(central)

                        # sauvegarde
                        chemin = geompath + str(edgeprevious) + ".csv"
                        f = open(chemin, 'w')
                        f.write("EDGE_ID;TRACKS_SIZE;WKT\n")
                        f.write(str(edgeprevious) + ";" + str(len(TRACES)) + ";" + central.toWKT() + "\n")
                        f.close()

                TRACES = []

            tid = line[1]
            mid = line[2]
            wkt = line[3]
            track = tkl.TrackReader.parseWkt(wkt)
            track.tid = mid
            track.uid = tid
            # print (track.uid, track.size(), edgeid)
            if track.size() > 3:
                TRACES.append(track)

            edgeprevious = edgeid


    # dernière trace
    if len(TRACES) >= 1:
        e = network.EDGES[edgeprevious]
        if e.geom.length() <= SEARCH:
            print ("    No merge for arc number (length too small):", edgeprevious)
            central = e.geom.copy()
            central.createAnalyticalFeature('edgeid', edgeprevious)
            central.tid = edgeprevious
            fusions.addTrack(central)

            # sauvegarde
            chemin = geompath + str(edgeprevious) + ".csv"
            f = open(chemin, 'w')
            f.write("EDGE_ID;TRACKS_SIZE;WKT\n")
            f.write(str(edgeprevious) + ";" + str(len(TRACES)) + ";" + central.toWKT() + "\n")
            f.close()

        else:
            print ("    Aggregation for arc number:", edgeprevious)
            central = _fusion(e, TRACES, SEARCH)
            MIN = min([MIN, len(TRACES)])
            MOY += len(TRACES)
            if len(TRACES) > 30:
                NBAP30 += 1
            else:
                NBAM30 += 1
            if central is not None:
                central.createAnalyticalFeature('edgeid', edgeprevious)
                central.tid = edgeprevious
                fusions.addTrack(central)
        
                # sauvegarde
                chemin = geompath + str(edgeprevious) + ".csv"
                f = open(chemin, 'w')
                f.write("EDGE_ID;TRACKS_SIZE;WKT\n")
                f.write(str(edgeprevious) + ";" + str(len(TRACES)) + ";" + central.toWKT() + "\n")
                f.close()


    print ('    Number of aggregations:', fusions.size())
    print ("    Number of aggregations with 30 traces:", NBAP30)
    print ("    Number of aggregations with fewer than 30 traces:", NBAM30)
    print ("    Minimum number of traces in aggregation:", MIN)
    if fusions.size() == 0:
        avg = 0
    else:
        avg = round(MOY/fusions.size())
    print ("    Average number of traces in aggregation:", avg)
    print ("    Aggregation process finished.")

    t1 = time.time()
    total = t1-t0
    print ("    Execution time (seconds):", total)
    t0 = t1

    try:
        log_event(RESPATH + "aggregate" + str(prefix) + ".json", {
            "Number of aggregations": fusions.size(),
            "Number of aggregations with 30 traces": NBAP30,
            "Number of aggregations with fewer than 30 traces": NBAM30,
            "Minimum number of traces in aggregation": MIN,
            "Average number of traces in aggregation": avg,
            "ts": time.time()
        })
    except Exception as e:
        print (e)
        print ('Error while writing aggregate information to log.')


    # =========================================================================
    # Raccord

    print ("Starting conflation ...")

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

    print ("    Conflation process finished.")

    t1 = time.time()
    total = t1-t0
    print ("    Execution time (seconds):", total)
    t0 = t1


    # =========================================================================
    # Fin
    
    print ("Stage 4 completed: map-matching, aggregation, and conflation.")

    


def _fusion (e, TRACES, SEARCH):
    '''

    '''

    rec = 10
    cv  = 1e-3

    if len(TRACES) <= 0:
        return None

    candidats = tkl.TrackCollection()
    for track in TRACES:
        t = tkl.simplify(track, tolerance=0.5,
                         mode=tkl.MODE_SIMPLIFY_DOUGLAS_PEUCKER,
                         verbose=False)
        candidats.addTrack(t)


    NB = candidats.size()
    # print ('        Number of traces to merge (before sampling):', NB)
    if NB > 30:
        collection = candidats.randNTracks(min(NB, 30))
    else:
        collection = candidats


    # print ('        Number of candidates in the aggregation process:', collection.size())
    print ('        Number of candidate tracks / number of sampled tracks',
           NB, "/", collection.size())

    if collection.size() > 1:
        # print ('        Launching Aggregation ...')
        centralDTW = tkl.fusion(collection,
                             master=tkl.MODE_MASTER_MEDIAN_LEN,
                             dim=2,
                             mode=tkl.MODE_MATCHING_FDTW,
                             p=2,
                             represent_method=tkl.MODE_REP_BARYCENTRE,
                             agg_method=tkl.MODE_AGG_MEDIAN,
                             constraint=False,
                             verbose=False,
                             iter_max=25,
                             recursive=rec,
                             cv=cv)
        # print ('        Aggregation ended.')
        return centralDTW
    elif candidats.size() == 1:
        print ('    Only one trajectory available for aggregation: no processing required')
        centralDTW = candidats.getTrack(0)
        return centralDTW

    return None






