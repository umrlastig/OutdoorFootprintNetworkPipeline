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
from pipeline import conflateOnNetwork



def createNetworkGeom (RESPATH, SEARCH, NB_OBS_MIN, DIST_MAX_2OBS, prefix='PT',
                       pathtraces='resample_fusion', pathtmm='tmm', pathfusion='fusion',
                       pathraccord='raccord'):

    t0 = time.time()

    main_text   = "--------------------------------------------------------------------------------------\r\n"
    main_text  += " ETAPE 4 :                                                               \r\n"
    main_text  += "   - Attribue les points des traces brutes à chaque arc de la topologie \r\n"
    main_text  += "   - Reconstruit les bons morceaux de traces candidats pour chaque arc de la topologie\r\n"
    main_text  += "   - Agrégation des morceaux de traces\r\n"
    main_text  += "   - Conflation des traces fusionnées afin d’obtenir un réseau de mobilité\r\n"
    main_text  += "--------------------------------------------------------------------------------------\r\n"
    main_text  += "--------------------------------------------------------------------------------------\r\n"
    print (main_text, end='')


    # =========================================================================
    #    Lecture du réseau
    #
    print ('Loading network ......')
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

    
    # =========================================================================
    #   Lecture des traces découpées et ré-échantillonnées.
    #
    print ('Loading collection of tracks ......')
    fmt = tkl.TrackFormat({'ext': 'CSV',
                           'srid': 'ENU',
                           'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                           'time_fmt': '2D/2M/4Y 2h:2m:2s',
                           'separator': ';',
                           'header': 0,
                           'cmt': '#',
                           'read_all': True})
    tracespath = RESPATH + '/' + pathtraces + '/'
    collection2 = tkl.TrackReader.readFromFile(tracespath, fmt)
    print ('    Number of tracks:', collection2.size())

    collection = tkl.TrackCollection()
    for trace in collection2:
        num = trace.getObsAnalyticalFeature('num', 0)
        track_id = trace.getObsAnalyticalFeature('track_id', 0)
        user_id = trace.getObsAnalyticalFeature('user_id', 0)
        version = trace.getObsAnalyticalFeature('version', 0)

        trace.uid = user_id
        trace.tid = str(num) + '-' + version
        #if str(trace.tid) == '6732043.0-v1' or str(trace.tid) == '6732043.0-v1':
        #if str(trace.tid) == '253623.0-v1':
        #if str(trace.tid) == '8195702.0-v1':
        #if str(trace.tid) == '14971357.0-v2':
        #if str(trace.tid) == '8195702.0-v1':
        #if str(trace.tid) == '12449457.0-v1':
        #print (trace.toWKT())
        #if str(trace.tid) == '2386441.0-v1':
        # print (trace.toWKT())
        collection.addTrack(trace)
    

    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)
    t0 = t1


    # =========================================================================
    #     Map-matching
    #

    si = tkl.SpatialIndex(network, verbose=False)
    network.spatial_index = si

    # Computes all distances between pairs of nodes
    network.prepare()

    # Map track on network
    print ('Launching Map-matching ...')
    tkl.mapOnNetwork(collection, network, search_radius=SEARCH, debug=False)
    print ('Map-matching ended')


    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)
    t0 = t1


    # =========================================================================
    #  Réultats Map-matching
    #

    # On construit un dictionnaire qui va contenir l'ensemble des points MM
    #    avec  leurs séquences afin de reconstuire des traces candidates
    #    pour la fusion:
    #        la trace doit être proche de la source de l'arc et
    #                           proche de la target de l'arc
    #        sans trou (index manquant)
    #        géométrie dans le même que celui de l'arc
    #
    MM = {}   #  [ide][pkid] : liste des observations

    for i in range(collection.size()):
        track = collection.getTrack(i)
        track.createAnalyticalFeature('mmtype', 'NOT')
        track.createAnalyticalFeature('idedge', -1)
        pkid = track.tid
    
        for j in range(track.size()):

            pb  = track[j].position
            ds = float(track["hmm_inference", j][2])
            dt = float(track["hmm_inference", j][3])
            idxedge = int(track["hmm_inference", j][1])

            edgeid = network.getEdgeId(idxedge)
            e = network.EDGES[edgeid]

            # if edgeid == '9476':
            #    print (e.geom.toWKT())
    
            if idxedge == -1:
                track.setObsAnalyticalFeature('mmtype', j, 'NOT')
                track.setObsAnalyticalFeature('idedge', j, -1)
            elif ds > 0.01 and dt > 0.01:
                if edgeid not in MM:
                    MM[edgeid] = {}
                if pkid not in MM[edgeid].keys():
                    MM[edgeid][pkid] = []
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

    print ('Map-matching results restructuring completed.')
    #print (MM['9476'])



    af_names = ['num', 'track_id', 'user_id', 'hmm_inference', 'mmtype', 'idedge']
    mmtracespath = RESPATH + 'mapmatch/' + pathtmm + '/'
    tkl.TrackWriter.writeToFiles(collection, mmtracespath,
                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                 h=1, separator=";", af_names=af_names)



    # =========================================================================
    #  On prépare les traces pour la fusion:
    #      - créer des morceaux
    #      - toutes les traces dans le même sens
    #  On enregistre le MM dans un fichier CSV

    # EDGE_ID;TRACK_ID;WKT

    mmpath = RESPATH + 'mapmatch/resultmm_' + prefix + '.csv'
    allmmpath = RESPATH + 'mapmatch/resultallmm_' + prefix + '.csv'
    f1 = open(mmpath,'w')
    f1.write("EDGE_ID;TRACK_ID;WKT\n")
    f2 = open(allmmpath,'w')
    f2.write("EDGE_ID;TRACK_ID;WKT\n")

    for edgeid, tobstrack in MM.items():
        e = network.EDGES[edgeid]
        for trackid, tobs in tobstrack.items():
            points_sorted = sorted(tobs, key=lambda x: x[0])

            regrouper = tkl.TrackCollection()

            tn = tkl.Track()
            v = 1
            p1 = None
            idxp1 = -1
            for p in points_sorted:
                idxp2 = p[0]
                p2 = p[1]
                if p1 is not None:
                    if idxp1 + 1 < idxp2:
                        # On coupe la trace pour créer un nouveau morceau ?
                        # Oui si zone de départ/arrivée
                        cb = candidates_for_aggregate(tn, e, SEARCH)
                        if cb.size() <= 0:
                            regrouper.addTrack(tn)
                        for tb in cb:
                            if tb.size() < NB_OBS_MIN:
                                continue
                            tid = str(trackid) + "-m" + str(v)
                            v += 1
                            f1.write(str(edgeid) + ";" + str(tid) + ";" + tb.toWKT() + "\n")

                        # On garde la trace de la trace sans regarder si c'est un bon candidat
                        f2.write(str(edgeid) + ";" + str(trackid) + ";" + tn.toWKT() + "\n")

                        tn = tkl.Track()
                        p1 = None

                tn.addObs(tkl.Obs(p2, tkl.ObsTime()))
                p1 = p2
                idxp1 = p[0]


            # dernier morceau de trace
            cb = candidates_for_aggregate(tn, e, SEARCH)
            if cb.size() <= 0:
                regrouper.addTrack(tn)
            for tb in cb:
                if tb.size() < NB_OBS_MIN:
                    continue
                tid = str(trackid) + "-v" + str(v)
                v += 1
                f1.write(str(edgeid) + ";" + str(tid) + ";" + tb.toWKT() + "\n")

            f2.write(str(edgeid) + ";" + str(trackid) + ";" + tn.toWKT() + "\n")


            # On regarde si on peut regrouper des traces
            fusionnees = getMerges(e, regrouper, DIST_MAX_2OBS)
            for t in fusionnees:
                cb = candidates_for_aggregate(t, e, SEARCH)
                for tb in cb:
                    if tb.size() < NB_OBS_MIN:
                        continue
                    tid = str(trackid) + "-m" + str(v)
                    v += 1
                    f1.write(str(edgeid) + ";" + str(tid) + ";" + tb.toWKT() + "\n")


    f1.close()
    f2.close()

    print ("Mapmatched step completed")

    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)
    t0 = t1

    # =========================================================================
    #     Fusion
    #

    print ("Starting aggregation ...")

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
        
            edgeid = line[0]
            e = network.EDGES[edgeid]

            if edgeprevious != edgeid:
                if edgeprevious != -1 and len(TRACES) > 1:
                    print ("Fusion pour le edge :", edgeprevious)
                    central = _fusion(e, TRACES, SEARCH)
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
        central = _fusion(e, TRACES, SEARCH)
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


    print ('Number of aggregations: ', fusions.size())
    print ("Aggregation process finished.")

    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)
    t0 = t1


    # =========================================================================
    # Raccord


    conflated = conflateOnNetwork(fusions, network, threshold=50, h=30)

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


    print ("Conflation process finished.")

    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)
    t0 = t1

    print ("Stage 4 finished: mapmatching, aggregation, conflation.")




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
    print ('    Nombre de traces à fusionner (avant le tirage):', NB)
    if NB > 30:
        collection = candidats.randNTracks(min(NB, 30))
    else:
        collection = candidats

    '''
    if collection is None:
        return None
    if not isinstance(collection, tkl.TrackCollection):
        return None
    if collection.size() <= 0:
        return None
    '''

    print ('    Number of candidates in the aggregation process:', collection.size())

    if collection.size() > 1:
        print ('Launching Aggregation ......')
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
        print ('Aggregation ended')
        return centralDTW
    elif candidats.size() == 1:
        centralDTW = candidats.getTrack(0)
        return centralDTW

    return None




def candidates_for_aggregate(track_segment, edge, SEARCH):
    '''
    Fonction utilitaire.
    
    tn : trace dont on a gardé l'ensemble des points consécutifs 
         recalés sur le troncon edge
    
    tn est decoupe si après une première longueur la trace quitte l'arrivée
    (cas d'un aller-retour sur le troncon)
    
    Les pauses au milieu ne sont pas gérées

    Une trace est gardée pour la fusion si :
        - son point de départ est "proche" de la source de l'arc. 
        - son point d'arrivée est "proche" de la target de l'arc.
        - sa géométrie dans le même sens que celui de l'arc.

    Si trop petite, on ne garde pas
    
    Si pas assez de points, on fait un resample de 1m
        
    '''

    morceaux = tkl.TrackCollection()

    s = edge.source.coord
    t = edge.target.coord

    # Est-ce que le début de la trace est dans une zone de départ ou d'arrivée ?
    # sinon on coupe le premier morceau

    BEGIN = 0
    END = track_segment.size() - 1
    
    Zone = 'N'
    p1 = track_segment.getFirstObs().position
    if p1.distance2DTo(s) < SEARCH:
        Zone = 'S'
    if p1.distance2DTo(t) < SEARCH:
        Zone = 'T'

    while p1.distance2DTo(s) >= SEARCH and p1.distance2DTo(t) >= SEARCH:
        BEGIN += 1
        if BEGIN > END-1:
            break
        p1 = track_segment.getObs(BEGIN).position
        if p1.distance2DTo(t) < SEARCH:
            Zone = 'T'
        if p1.distance2DTo(s) < SEARCH:
            Zone = 'S'

    if Zone == 'N':
        # Aucun des points n'est dans la zone de départ ou d'arrivée
        #if edge.id == "9476":
        #    print ('---------', edge.id, Zone, BEGIN)
        # print (track_segment.toWKT())
        return morceaux

    if BEGIN > 0:
        # Il faut retirer le premier morceau de la trace qui est hors définition
        # d'une trace candidate
        track_segment = track_segment.extract(BEGIN, END)

    if track_segment.size() <= 0:
        # On ne fait rien, trace à ne pas garder pour la fusion
        # print ('Pas de candidat pour le segment')
        return morceaux

    if Zone == 'T':
        # On retourne la trace
        new_track_segment = track_segment.reverse()
        p1 = new_track_segment.getFirstObs().position
        if p1.distance2DTo(t) < SEARCH:
            Zone = 'T'
        elif p1.distance2DTo(s) < SEARCH:
            Zone = 'S'
        else:
            Zone = 'N'
    else:
        new_track_segment = track_segment

    if Zone == 'N':
        # Aucun des points n'est dans la zone de départ ou d'arrivée
        return morceaux

    p2 = new_track_segment.getLastObs().position

    #if edge.id == "11338":
    #    print ('---------', edge.id, Zone)

    # On sait que le début est dans une zone,
    # on regarde la fin et aussi on s'occupe du sens d'orientation du
    # premier morceau
    '''
    p2 = track_segment.getLastObs().position
    if p1.distance2DTo(s) >= SEARCH:
        if p2.distance2DTo(s) < SEARCH:
            # sens inverse
            track_segment = track_segment.reverse()
            p1 = track_segment.getFirstObs().position
            p2 = track_segment.getLastObs().position
        else:
            print ('---????')
            # on fait rien, trace à ne pas garder pour la fusion
            # print ('Pas de candidat pour le segment')
            return morceaux
    else:
        print('!,!,!,')
    '''

    # -------------------------------------------------------------------------
    # On découpe si besoin
    atteint = False
    dd = 0
    start = Zone
    for idx, o in enumerate(new_track_segment):

        if start == 'S' and o.position.distance2DTo(t) < SEARCH:
            atteint = True

        if start == 'T' and o.position.distance2DTo(s) < SEARCH:
            atteint = True

        if atteint and o.position.distance2DTo(t) > SEARCH and start == 'S':
            # la deuxième partie de la trace est sortie
            morceau = new_track_segment.extract(dd, idx-1)
            morceaux.addTrack(morceau)
            dd = idx
            atteint = False
            start = 'T'

        if atteint and o.position.distance2DTo(s) > SEARCH and start == 'T':
            # la deuxième partie de la trace est sortie
            morceau = new_track_segment.extract(dd, idx-1).reverse()
            morceaux.addTrack(morceau)
            dd = idx
            atteint = False
            start = 'S'

    if atteint:
        morceau = new_track_segment.extract(dd, idx)
        if start == 'T':
            morceaux.addTrack(morceau.reverse())
        else:
            morceaux.addTrack(morceau)


    if edge.geom.length() < 2*SEARCH:
        for morceau in morceaux:
            morceau.resample(1, mode=tkl.MODE_SPATIAL)

    return morceaux

def sommets_proches(t1, t2, DIST_MAX_2OBS):
    p1 = t1.getFirstObs()
    p2 = t1.getLastObs()

    o1 = t2.getFirstObs()
    o2 = t2.getLastObs()

    if o1.distance2DTo(p1) < DIST_MAX_2OBS and o2.distance2DTo(p2) < DIST_MAX_2OBS:
        return False
    if o2.distance2DTo(p1) < DIST_MAX_2OBS and o1.distance2DTo(p2) < DIST_MAX_2OBS:
        return False

    if o1.distance2DTo(p1) < DIST_MAX_2OBS:
        return True
    if o2.distance2DTo(p1) < DIST_MAX_2OBS:
        return True
    if o1.distance2DTo(p2) < DIST_MAX_2OBS:
        return True
    if o2.distance2DTo(p2) < DIST_MAX_2OBS:
        return True
    return False


def merge(t1, t2, DIST_MAX_2OBS):
    p1 = t1.getFirstObs()
    p2 = t1.getLastObs()

    o1 = t2.getFirstObs()
    o2 = t2.getLastObs()

    if o1.distance2DTo(p1) < DIST_MAX_2OBS:
        return t1.reverse() + t2
    if o2.distance2DTo(p1) < DIST_MAX_2OBS:
        return t2 + t1
    if o1.distance2DTo(p2) < DIST_MAX_2OBS:
        return t1 + t2
    if o2.distance2DTo(p2) < DIST_MAX_2OBS:
        return t1 + t2.reverse()

    return None




def getMerges(edge, collection, DIST_MAX_2OBS):

    s = edge.geom.getFirstObs()
    t = edge.geom.getLastObs()
    

    TRAITEES = []
    for track in collection:
    
        PROXGROUPS = []
    
        # chercher les traces contenant des segments proches
        for t in TRAITEES:
            if sommets_proches(t, track, DIST_MAX_2OBS):
                PROXGROUPS.append(t)
                break
    
        if len(PROXGROUPS) == 0:
            # créer un nouveau groupe
            TRAITEES.append(track)
    
        elif len(PROXGROUPS) == 1:
            t1  = PROXGROUPS[0]
            TRAITEES.remove(t1)
            # ajouter au groupe existant
            newtrack = merge(t1, track, DIST_MAX_2OBS)
            TRAITEES.append(newtrack)
    
        else:
            # fusionner les groupes
            nouveau = track
            for t1 in PROXGROUPS:
                TRAITEES.remove(t1)
                newtrack = merge(t1, track, DIST_MAX_2OBS)
    
            TRAITEES.append(newtrack)

    return TRAITEES


