# -*- coding: utf-8 -*-

'''
        - 
'''


import sys
import csv
csv.field_size_limit(sys.maxsize)


import tracklib as tkl

from tracklib.util.qgis import QGIS, LineStyle, PointStyle
from PyQt5.QtGui import QColor




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
                t = t.reverse()
                candidats.addTrack(t)


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




def aggregation(RESPATH, SEARCH):

    print ("Lancement de l'agrégation")


    # =============================================================================
    #      Chargement du réseau
    #

    fmt = tkl.NetworkFormat({
           "pos_edge_id": 0,
           "pos_source": 1,
           "pos_target": 2,
           "pos_wkt": 4,
           "srid": "ENU",
           "header": 1})

    netwokpath = RESPATH + 'network/reseau.csv'
    network = tkl.NetworkReader.readFromFile(netwokpath, fmt)

    print ('Number of edges = ', len(network.EDGES))
    print ('Number of nodes = ', len(network.NODES))


    # =============================================================================
    #     Fusion
    #

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
                        f.write("EDGE_ID;WKT\n")
                        f.write(str(edgeid) + ";" + central.toWKT() + "\n")
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
            f.write("EDGE_ID;WKT\n")
            f.write(str(edgeid) + ";" + central.toWKT() + "\n")
            f.close()


    print ('Number of aggregations: ', fusions.size())
    if fusions.size() > 0:
        QGIS.plotTracks(fusions, type='LINE',
                        style=LineStyle.simpleVert1,
                        title='Fusions', AF=True)


    # =========================================================================


    print ("Fin de la fusion.")
    print ("END SCRIPT 6.")




