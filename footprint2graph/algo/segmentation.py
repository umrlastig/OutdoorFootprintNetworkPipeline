# -*- coding: utf-8 -*-

import time

import tracklib as tkl
from footprint2graph import log_event



def candidates_for_aggregate(track_segment, edge, BUFFER):
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
    if p1.distance2DTo(s) < BUFFER:
        Zone = 'S'
    if p1.distance2DTo(t) < BUFFER:
        Zone = 'T'

    while p1.distance2DTo(s) >= BUFFER and p1.distance2DTo(t) >= BUFFER:
        BEGIN += 1
        if BEGIN > END-1:
            break
        p1 = track_segment.getObs(BEGIN).position
        if p1.distance2DTo(t) < BUFFER:
            Zone = 'T'
        if p1.distance2DTo(s) < BUFFER:
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
        if p1.distance2DTo(t) < BUFFER:
            Zone = 'T'
        elif p1.distance2DTo(s) < BUFFER:
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
    if p1.distance2DTo(s) >= BUFFER:
        if p2.distance2DTo(s) < BUFFER:
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

        if start == 'S' and o.position.distance2DTo(t) < BUFFER:
            atteint = True

        if start == 'T' and o.position.distance2DTo(s) < BUFFER:
            atteint = True

        if atteint and o.position.distance2DTo(t) > BUFFER and start == 'S':
            # la deuxième partie de la trace est sortie
            morceau = new_track_segment.extract(dd, idx-1)
            morceaux.addTrack(morceau)
            dd = idx
            atteint = False
            start = 'T'

        if atteint and o.position.distance2DTo(s) > BUFFER and start == 'T':
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


    if edge.geom.length() < 2*BUFFER:
        for morceau in morceaux:
            morceau.resample(1, mode=tkl.MODE_SPATIAL)

    return morceaux





def getcandidates(MM, network, collection, BUFFER=15, RESPATH=None, prefix=None):


    # =========================================================================
    # =========================================================================
    #  On prépare les traces pour la fusion:
    #      - créer des morceaux
    #      - toutes les traces dans le même sens
    #  On enregistre le MM dans un fichier CSV

    # EDGE_ID;TRACK_ID;WKT

    print ('Starting construction of candidate trajectory segments for each topology edge ...')

    if RESPATH is not None:
        mmpath = RESPATH + 'mapmatch/resultmm_' + str(prefix) + '.csv'
        allmmpath = RESPATH + 'mapmatch/resultallmm_' + str(prefix) + '.csv'
        f1 = open(mmpath,'w')
        f1.write("EDGE_ID;TRACK_ID;OFNP_ID;WKT\n")
        f2 = open(allmmpath,'w')
        f2.write("EDGE_ID;TRACK_ID;WKT\n")


    TRACES = {}
    MIN = 100000
    MAX = 0
    NBC = 0
    MOYC = 0
    for edgeid, tobstrack in MM.items():
        # print (edgeid)
        #if edgeid != '23':
        #    continue

        if not edgeid in TRACES:
            TRACES[edgeid] = []

        e = network.EDGES[edgeid]
        for trackid, tobs in tobstrack.items():
            #if trackid != "OV_3901-v1_v1-v1":
            #    continue
            #print ('------')
            #if trackid != '121.0-v1':
            #    continue

            #print (tobs)

            track = collection.getTrackWithTid(trackid)
            tid = str(int(track.getObsAnalyticalFeature('TID', 0)))
            mid = str(track.getObsAnalyticalFeature('MID', 0))
            #print ('------')
            points_sorted = sorted(tobs, key=lambda x: x[0])

            regrouper = tkl.TrackCollection()
            tn = tkl.Track()
            v = 1
            p1 = None
            idxp1 = -1
            for p in points_sorted:
                idxp2 = p[0]
                #print (idxp2)
                p2 = p[1]
                if p1 is not None:
                    if idxp1 + 1 < idxp2:
                        #print ('?!?!?!?!?!?!?!?!?!?!', idxp1, idxp2, tn.size())
                        # On coupe la trace pour créer un nouveau morceau ?
                        # Oui si zone de départ/arrivée
                        cb = candidates_for_aggregate(tn, e, BUFFER)
                        if cb.size() <= 0:
                            regrouper.addTrack(tn)
                        for tb in cb:
                            # if tb.size() < NB_OBS_MIN:
                            #    continue
                            # tid = str(trackid) + "-m" + str(v)
                            mid = mid + "-m" + str(v)
                            v += 1
                            if RESPATH is not None:
                                f1.write(str(edgeid) + ";" 
                                         + str(tid) + ";" + str(mid) + ";"
                                         + tb.toWKT() + "\n")
                            # print ('+++++', tb.size())
                            trace = tkl.TrackReader.parseWkt(tb.toWKT(), 'ENU')
                            trace.tid = mid
                            trace.uid = tid
                            trace.createAnalyticalFeature('TID', tid)
                            trace.createAnalyticalFeature('MID', mid)
                            TRACES[edgeid].append(trace)

                        if RESPATH is not None:
                            # On garde la trace de la trace sans regarder si c'est un bon candidat
                            f2.write(str(edgeid) + ";" + str(trackid) + ";" + tn.toWKT() + "\n")

                        tn = tkl.Track()
                        p1 = None
                        idxd = 0

                tn.addObs(tkl.Obs(p2, tkl.ObsTime()))
                p1 = p2
                idxp1 = idxp2


            # dernier morceau de trace
            #print (tn.size())
            cb = candidates_for_aggregate(tn, e, BUFFER)
            # print (cb.size())
            if cb.size() <= 0:
                regrouper.addTrack(tn)
            for tb in cb:
                #if tb.size() < NB_OBS_MIN:
                #    continue
                # tid = str(trackid) + "-v" + str(v)
                mid = mid + "-m" + str(v)
                v += 1
                if RESPATH is not None:
                    f1.write(str(edgeid) + ";" 
                             + str(tid) + ";" + str(mid) + ";"
                             + tb.toWKT() + "\n")
                #print ('+++++')
                trace = tkl.TrackReader.parseWkt(tb.toWKT(), 'ENU')
                trace.tid = mid
                trace.uid = tid
                trace.createAnalyticalFeature('TID', tid)
                trace.createAnalyticalFeature('MID', mid)
                TRACES[edgeid].append(trace)

            if RESPATH is not None:
                f2.write(str(edgeid) + ";" + str(trackid) + ";" + tn.toWKT() + "\n")

        n = len(TRACES[edgeid])
        print ('   ', n, ' candidates for edge', edgeid)
        NBC += 1
        MIN = min([MIN,n])
        MAX = max([MAX,n])
        MOYC += n


    if RESPATH is not None:
        f1.close()
        f2.close()

    try:
        print ("    Number of processed edges: ", NBC)
        print ("    Minimum number of candidate tracks per edge: ", MIN)
        print ("    Maximum number of candidate traces per edge: ", MAX)
        print ("    Average number of candidate tracks per edge: ", round(MOYC/NBC))

        log_event(RESPATH + "candidate" + str(prefix) + ".json", {
            "Number of processed edges": NBC,
            "Minimum number of candidate traces per edge": MIN,
            "Maximum number of candidate traces per edge": MAX,
            "Average number of candidate tracks per edge": round(MOYC/NBC),
            "ts": time.time()
        })
    except Exception as e:
        print (e)
        print ('Error while writing candidate information to log.')

    print ("    Segment construction completed.")

    return TRACES




