# -*- coding: utf-8 -*-


import sys
import csv
csv.field_size_limit(sys.maxsize)

import matplotlib.pyplot as plt
import tracklib as tkl



def bonneTrace(tn, edge, NB_OBS_MIN, SEARCH):
        '''
        Fonction utilitaire.
        Une trace est gardée pour la fusion si son point de départ est "proche" 
        d'un noeud de l'arc et son point d'arrivée est "proche" de l'autre noeud de l'arc.
        '''

        morceaux = tkl.TrackCollection()

        if tn.size() >= NB_OBS_MIN:

            p1 = tn.getFirstObs().position
            p2 = tn.getLastObs().position

            s = edge.source.coord
            t = edge.target.coord

            if edge.geom.length() < SEARCH:
                if p1.distance2DTo(s) < SEARCH/2 and p2.distance2DTo(t) < SEARCH/2:
                    morceaux.addTrack(tn)
                if p1.distance2DTo(t) < SEARCH/2 and p2.distance2DTo(s) < SEARCH/2:
                    morceaux.addTrack(tn.reverse())
            else:

                if p1.distance2DTo(s) < SEARCH/2:
                    reverse = False
                    atteint = False
                    dd = 0
                    for idx, o in enumerate(tn):
                        if o.position.distance2DTo(t) < SEARCH/2:
                            atteint = True
                        if atteint and o.position.distance2DTo(t) > SEARCH/2:
                            # la deuxième partie de la trace est sortie
                            t1 = tn.extract(dd, idx-1)
                            dd = idx
                            morceaux.addTrack(t1)
                            t = s
                            s = o.position
                            atteint = False
                            reverse = True
                    if atteint:
                        t1 = tn.extract(dd, idx)
                        if reverse:
                            morceaux.addTrack(t1.reverse())
                        else:
                            morceaux.addTrack(t1)


                if p2.distance2DTo(s) < SEARCH/2:
                    tnr = tn.reverse()
                    reverse = False
                    atteint = False
                    dd = 0
                    for idx, o in enumerate(tnr):
                        if o.position.distance2DTo(t) < SEARCH/2:
                            atteint = True
                        if atteint and o.position.distance2DTo(t) > SEARCH/2:
                            # la deuxième partie de la trace est sortie
                            t1 = tn.extract(dd, idx-1)
                            dd = idx
                            morceaux.addTrack(t1)
                            t = s
                            s = o.position
                            atteint = False
                            reverse = True
                    if atteint:
                        t1 = tnr.extract(dd, idx)
                        if reverse:
                            morceaux.addTrack(t1.reverse())
                        else:
                            morceaux.addTrack(t1)

        return morceaux


RESPATH = r'/home/md_vandamme/4_RESEAU/ExampleZ1Walk/'
fmt = tkl.NetworkFormat({
       "pos_edge_id": 0,
       "pos_source": 1,
       "pos_target": 2,
       "pos_wkt": 4,
       "srid": "ENU",
       "header": 1})

netwokpath = RESPATH + 'network/reseau.csv'
network = tkl.NetworkReader.readFromFile(netwokpath, fmt)


SEARCH = 25
edge = network.EDGES['19364']
NB_OBS_MIN = 10


#  FAUX  : 1151
# COUPER : 987, 948, 581

cptLigne = 0
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
        if edgeid == '19364':
            wkt = line[2]
            tn = tkl.TrackReader.parseWkt(wkt)
            morceaux = bonneTrace(tn, edge, NB_OBS_MIN, SEARCH)

            for t in morceaux:
                pt = morceaux[0].getFirstObs().position
                plt.plot(pt.getX(), pt.getY(), 'bo', markersize=10)
                cptLigne += 1

print (cptLigne)
plt.xlim([950947,  951050])
plt.ylim([6512671, 6513090])
plt.show()















