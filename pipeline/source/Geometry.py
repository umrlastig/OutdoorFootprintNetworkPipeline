# -*- coding: utf-8 -*-

'''
    Recalage des points sur le réseau
'''

import sys
import csv
csv.field_size_limit(sys.maxsize)

import tracklib as tkl

from util.KitFusion import bonneTrace




def createNetworkGeom(RESPATH, SEARCH, DIST_MAX_2OBS, NB_OBS_MIN):

    # =============================================================================
    #    Lecture du réseau
    #
    fmt = tkl.NetworkFormat({
           "pos_edge_id": 0,
           "pos_source": 1,
           "pos_target": 2,
           "pos_wkt": 4,
           "srid": "ENU",
           "separator": ",",
           "header": 1})
    
    netwokpath = RESPATH + 'network/reseau.csv'
    network = tkl.NetworkReader.readFromFile(netwokpath, fmt)
    
    print ('Number of edges = ', len(network.EDGES))
    print ('Number of nodes = ', len(network.NODES))


    # =============================================================================
    #   Lecture des traces découpées et ré-échantillonnées.
    #
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

    cptId = 1
    collection = tkl.TrackCollection()
    for trace in collection2:
        trace.uid = cptId
        trace.tid = cptId
        cptId += 1
        collection.addTrack(trace)
    



    # =============================================================================
    #     Map-matching
    #

    MM = {}   #  [ide][pkid] : liste des observations

    network.simplify(0, tkl.MODE_SIMPLIFY_REM_POS_DUP, verbose=False)
    network.simplify(5, tkl.MODE_SIMPLIFY_DOUGLAS_PEUCKER, verbose=False)

    si = tkl.SpatialIndex(network, verbose=False)
    network.spatial_index = si


    # Computes all distances between pairs of nodes
    network.prepare()


    # Map track on network
    print ('Launching Map-matching')
    tkl.mapOnNetwork(collection, network, search_radius=SEARCH, debug=False)
    print ('Map-matching ended')


    # =============================================================================
    #     Stats Map-matching
    #

    for i in range(collection.size()):
        track = collection.getTrack(i)
        pkid = track.tid
    
        for j in range(track.size()):
            pb  = track[j].position
            # mm  = track["hmm_inference", j][0]

            ds = float(track["hmm_inference", j][2])
            dt = float(track["hmm_inference", j][3])

            idxedge = track["hmm_inference", j][1]
            edgeid = network.getEdgeId(idxedge)
            e = network.EDGES[edgeid]
    
            if idxedge != -1 and ds > 0.01 and dt > 0.01:
                if edgeid not in MM:
                    MM[edgeid] = {}
                if pkid not in MM[edgeid].keys():
                    MM[edgeid][pkid] = []
                MM[edgeid][pkid].append((j,pb))
            elif abs(ds) < 0.01:
                idnode = e.source.id
                edgesid = network.getIncidentEdges(idnode)
                for eid in edgesid:
                    if eid not in MM:
                        MM[eid] = {}
                    if pkid not in MM[eid].keys():
                        MM[eid][pkid] = []
                    MM[eid][pkid].append((j,pb))
            elif abs(dt) < 0.01:
                idnode = e.target.id
                edgesid = network.getIncidentEdges(idnode)
                for eid in edgesid:
                    if eid not in MM:
                        MM[eid] = {}
                    if pkid not in MM[eid].keys():
                        MM[eid][pkid] = []
                    MM[eid][pkid].append((j,pb))
    
    print ('Stats computing ended.')
    



    # =============================================================================
    #  On prépare les traces pour la fusion:
    #     - créer des morceaux
    #     - toutes les traces dans le même sens
    # on enregistre le MM dans un fichier CSV
    
    mmpath = RESPATH + 'mapmatch/resultmm.csv'

    NBPasBonne = 0

    f = open(mmpath,'w')
    f.write("EDGE_ID;TRACK_ID;WKT\n")

    for edgeid, tobstrack in MM.items():
        e = network.EDGES[edgeid]

        for trackid, tobs in tobstrack.items():
            points_sorted = sorted(tobs, key=lambda x: x[0])
    
            tn = tkl.Track()
            p1 = None
            for p in points_sorted:
                p2 = p[1]
                if p1 is not None:
                    if p2.distance2DTo(p1)> DIST_MAX_2OBS:
                        # on coupe la trace pour créer un nouveau morceau
                        cb = bonneTrace(tn, e, NB_OBS_MIN, SEARCH)
                        for tb in cb:
                            f.write(str(edgeid) + ";" + str(trackid) + ";" + tb.toWKT() + "\n")
                        if cb.size() <= 0:
                            NBPasBonne += 1
                        tn = tkl.Track()
                tn.addObs(tkl.Obs(p2, tkl.ObsTime()))
                p1 = p2

            # dernier morceau de trace
            cb = bonneTrace(tn, e, NB_OBS_MIN, SEARCH)
            for tb in cb:
                f.write(str(edgeid) + ";" + str(trackid) + ";" + tn.toWKT() + "\n")
            if cb.size() <= 0:
                NBPasBonne += 1

    f.close()


    txtpath = r"file:///" + mmpath + "?delimiter=;&wktField=WKT&crs=EPSG:2154"
    print ('Nombre de traces rejetées : ', NBPasBonne)

    print ("Fin de la partie de recalage.")




    # =============================================================================
    #     Fusion
    #

    print ("Lancement de l'agrégation")

    geompath = RESPATH + 'geometry/'

    # Aggregation with DTW distance
    fusions = tkl.TrackCollection()
    edgeprevious = -1
    TRACES = []
    mmpath = RESPATH + 'mapmatch/resultmm.csv'
    with open(mmpath, 'r') as file:
        cpt = 0
        for s in file:

            if cpt == 0:
                cpt += 1
                continue

            line = s.split(";")
            if len(line) < 1:
                continue
        
            edgeid = line[0]

            if edgeprevious != edgeid:
                if edgeprevious != -1 and len(TRACES) > 1:
                    print ("Fusion pour le edge :", edgeprevious)
                    central = _fusion(TRACES, SEARCH)
                    if central is not None:
                        central.createAnalyticalFeature('edgeid', edgeprevious)
                        fusions.addTrack(central)

                        # sauvegarde
                        chemin = geompath + str(edgeprevious) + ".csv"
                        f = open(chemin, 'w')
                        f.write("EDGE_ID;TRACKS_SIZE;WKT\n")
                        f.write(str(edgeprevious) + ";" + str(len(TRACES)) + ";" + central.toWKT() + "\n")
                        f.close()

                # if len(TRACES) > 1:
                TRACES = []
                # break

                # print ('Edge ', edgeid)



            trackid = line[1]
            wkt = line[2]

            track = tkl.TrackReader.parseWkt(wkt)
            if track.size() > 3:
                TRACES.append(track)

            edgeprevious = edgeid


    # dernière trace

    if len(TRACES) > 1:
        print ("Dernière fusion pour le edge :", edgeprevious)
        central = _fusion(TRACES, SEARCH)
        if central is not None:
            central.createAnalyticalFeature('edgeid', edgeprevious)
            fusions.addTrack(central)
    
            # sauvegarde
            chemin = geompath + str(edgeprevious) + ".csv"
            f = open(chemin, 'w')
            f.write("EDGE_ID;TRACKS_SIZE;WKT\n")
            f.write(str(edgeprevious) + ";" + str(len(TRACES)) + ";" + central.toWKT() + "\n")
            f.close()


    print ('Number of aggregations: ', fusions.size())
    if fusions.size() > 0:
        QGIS.plotTracks(fusions, type='LINE',
                        style=LineStyle.simpleVert1,
                        title='Fusions', AF=True)


    # =========================================================================


    print ("Fin de la fusion.")




def _fusion (TRACES, SEARCH):
    '''

    '''

    if len(TRACES) <= 0:
        return None

    candidatsMultiSens = tkl.TrackCollection(TRACES)
    if candidatsMultiSens is None:
        return None

    NB = candidatsMultiSens.size()
    print ('    Nombre de traces à fusionner (avant le tirage):', NB)

    if NB > 50:
        collection = candidatsMultiSens.randNTracks(min(NB,70))
    else:
        collection = candidatsMultiSens

    if collection is None:
        return None
    if not isinstance(collection, tkl.TrackCollection) and collection.size() <= 0:
        return None

    # Même sens
    candidats = tkl.TrackCollection()
    TREF = collection[0]
    for t1 in collection:

        t = tkl.simplify(t1, tolerance=0.5, mode=tkl.MODE_SIMPLIFY_DOUGLAS_PEUCKER, verbose=False)

        if t.length() < 2*SEARCH:
            d1 = tkl.compare(TREF, t, verbose=False, mode=tkl.MODE_COMPARISON_DTW, p=1)
            d2 = tkl.compare(TREF, t.reverse(), verbose=False, mode=tkl.MODE_COMPARISON_DTW, p=1)
            # A l'envers
            if (d2 < d1):
                t = t.reverse()
                candidats.addTrack(t)
            else:
                candidats.addTrack(t)
        else:
            p1 = t.getFirstObs().position
            p2 = t.getLastObs().position

            so = TREF.getFirstObs().position
            ta = TREF.getLastObs().position

            if p1.distance2DTo(so) < SEARCH and p2.distance2DTo(ta) < SEARCH:
                candidats.addTrack(t)
            elif p2.distance2DTo(so) < SEARCH and p1.distance2DTo(ta) < SEARCH:
                t1 = t.reverse()
                candidats.addTrack(t1)


    print ('    Nombre de traces à fusionner (après la direction):', candidats.size())
    if candidats.size() > 1:
        print ('Démarrage de la fusion ......')
        centralDTW = tkl.fusion(candidats,
                             master=tkl.MODE_MASTER_MEDIAN_LEN,
                             dim=2,
                             mode=tkl.MODE_MATCHING_DTW,
                             p=2,
                             represent_method=tkl.MODE_REP_BARYCENTRE,
                             agg_method=tkl.MODE_AGG_MEDIAN,
                             constraint=False,
                             verbose=False,
                             iter_max=25,
                             recursive=15)
        print ('Fin de la fusion.')
        return centralDTW

    elif candidats.size() == 1:
        centralDTW = candidats.getTrack(0)
        return centralDTW

    return None





