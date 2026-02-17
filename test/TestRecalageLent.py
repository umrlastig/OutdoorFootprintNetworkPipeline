# -*- coding: utf-8 -*-

import os
import tracklib as tkl


SEARCH        = 25

tracepath  = r'/home/md_vandamme/5_GPS/TMP/tracks/'
netwokpath = r'/home/md_vandamme/5_GPS/TMP/reseau.csv'


# -----------------------------------------------------------------------------
#   Chargement du réseau

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


# -----------------------------------------------------------------------------
#    Chargement des traces

fmt = tkl.TrackFormat({'ext': 'CSV',
                       'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': -1,
                       'srid': 'ENU',
                       'separator': ';',
                       'header': 0,
                       'cmt': '#',
                       'verbose': False})

LISTFILE = os.listdir(tracepath)
collection = tkl.TrackCollection()
for f in LISTFILE:
    trace = tkl.TrackReader.readFromFile(tracepath + f, fmt)
    trace.resample(1, tkl.MODE_SPATIAL)
    collection.addTrack(trace)
print ('Nombre de traces:', collection.size())



# -----------------------------------------------------------------------------
#     Map matching


MM = {}

si = tkl.SpatialIndex(network, verbose=False)
network.spatial_index = si


# Computes all distances between pairs of nodes
network.prepare()


# Map track on network
print ('Launching Map-matching')
tkl.mapOnNetwork(collection, network, search_radius=SEARCH, verbose=False)
print ('Map-matching ended')





















