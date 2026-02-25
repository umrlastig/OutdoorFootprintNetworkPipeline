# -*- coding: utf-8 -*-


import tracklib as tkl

from pipeline.util import filtreNoeudSimple, deleteSmallEdge


RESPATH = r'/home/md_vandamme/4_RESEAU/Ex2Z1Walk/'

seuil_doublon = 0.1
DIST_MIN_ARC  = 30

fmt = tkl.NetworkFormat({
       "pos_edge_id": 0,
       "pos_source": 1,
       "pos_target": 2,
       "pos_wkt": 4,
       "srid": "ENU",
       "separator": ",",
       "header": 1})

netwokpath = RESPATH + 'network/reseau1.csv'
network = tkl.NetworkReader.readFromFile(netwokpath, fmt)

print ('Number of edges = ', len(network.EDGES))
print ('Number of nodes = ', len(network.NODES))


# removeDuplicateGeometries(network, seuil_doublon)
# print ('Fin suppression des arcs en doublon 3/4.')


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

netwokpath = RESPATH + 'network/reseau2.csv'
tkl.NetworkWriter.writeToCsv(network, netwokpath)


