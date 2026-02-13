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


netwokpath          = r'/home/md_vandamme/4_RESEAU/ExampleTest/network/reseau.csv'
mmpath              = r'/home/md_vandamme/4_RESEAU/ExampleTest/mapmatch/resultmm.csv'
geompath            = r'/home/md_vandamme/4_RESEAU/ExampleTest/geometry/'


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

network = tkl.NetworkReader.readFromFile(netwokpath, fmt)

print ('Number of edges = ', len(network.EDGES))
print ('Number of nodes = ', len(network.NODES))




# =============================================================================
#     Fusion
#

def fusion (TRACES):
    candidatsMultiSens = tkl.TrackCollection(TRACES)
    if candidatsMultiSens.size() <= 0:
        return

    NB = candidatsMultiSens.size()
    print (NB, ' nombre de traces à fusionner')


    candidats = tkl.TrackCollection()
    TREF = candidatsMultiSens[0]
    for t in candidatsMultiSens:
        d1 = tkl.compare(TREF, t, verbose=False, mode=tkl.MODE_COMPARISON_DTW, p=1)
        d2 = tkl.compare(TREF, t.reverse(), verbose=False, mode=tkl.MODE_COMPARISON_DTW, p=1)
        # A l'envers
        if (d2 < d1):
            t = t.reverse()
            candidats.addTrack(t)
        else:
            candidats.addTrack(t)

    if candidats.size() > 1:
        NB = candidats.size()
        print (NB, ' nombre de traces à fusionner')
        print ('demarrage de la fusion')
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
                             recursive=18)
        print ('fin de la fusion')
        return centralDTW

    elif candidats.size() == 1:
        centralDTW = candidats.getTrack(0)
        return centralDTW

    return None


# Aggregation with DTW distance
fusions = tkl.TrackCollection()
edgeprevious = -1
TRACES = []
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

        if str(edgeid) != '13':
            continue

        if edgeprevious != edgeid:
            if edgeprevious != -1 and len(TRACES) > 1:
                print ("fusuion pour le edge :", edgeid)
                central = fusion(TRACES)
                central.createAnalyticalFeature('edgeid', str(edgeid))
                fusions.addTrack(central)

                # sauvegarde
                chemin = geompath + str(edgeid) + ".csv"
                f = open(chemin, 'w')
                f.write("EDGE_ID;WKT\n")
                f.write(str(edgeid) + ";" + central.toWKT() + "\n")
                f.close()

                # break

            # print ('Edge ', edgeid)
            TRACES = []

        trackid = line[1]
        wkt = line[2]

        track = tkl.TrackReader.parseWkt(wkt)
        if track.size() > 3:
            TRACES.append(track)

        edgeprevious = edgeid

# dernière trace

if len(TRACES) > 1:
    print ("fusuion pour le edge :", edgeid)
    central = fusion(TRACES)
    central.createAnalyticalFeature('edgeid', str(edgeid))
    fusions.addTrack(central)

    # sauvegarde
    chemin = geompath + str(edgeid) + ".csv"
    f = open(chemin, 'w')
    f.write("EDGE_ID;WKT\n")
    f.write(str(edgeid) + ";" + central.toWKT() + "\n")
    f.close()


print ('Number of aggregations: ', fusions.size())
if fusions.size() > 0:
    QGIS.plotTracks(fusions, type='LINE',
                    style=LineStyle.simpleVert1,
                    title='Fusions', AF=True)


# =============================================================================


print ("Fin de la fusion.")
print ("END SCRIPT 6.")




