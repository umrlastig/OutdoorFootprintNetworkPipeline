# -*- coding: utf-8 -*-

import os
import sys
import math
import random
import shapely
import numpy as np
import matplotlib.pyplot as plt

import tracklib as tkl
from pipeline import conflateOnNetwork

plt.figure(figsize=(12, 6))
plt.subplots_adjust(top=1.3, wspace=0.2, hspace=0.2)


netwokpath = '/home/md_vandamme/4_RESEAU/Ex2Z1Walk/network/reseau.csv'
fusionpath = '/home/md_vandamme/4_RESEAU/Ex2Z1Walk/geometry/fusion/'
raccordpath = '/home/md_vandamme/4_RESEAU/Ex2Z1Walk/geometry/raccord/'


# ===========================================================================

ax1 = plt.subplot2grid((1, 2), (0, 0))


# lire le réseau
fmt = tkl.NetworkFormat({
       "pos_edge_id": 0,
       "pos_source": 1,
       "pos_target": 2,
       "pos_wkt": 4,
       "srid": "ENU",
       "separator": ",",
       "header": 1})
network = tkl.NetworkReader.readFromFile(netwokpath, fmt, verbose=False)
print ('Number of edges = ', len(network.EDGES))
print ('Number of nodes = ', len(network.NODES))

network.plot(append=ax1)


# lire les traces fusionnées
fusions = tkl.TrackCollection()
for fusionfilename in os.listdir(fusionpath):
    with open(fusionpath + fusionfilename, 'r') as file:
        line = file.readline()
        line = file.readline()
        items = line.split(";")
        edge_id = items[0]
        wkt = items[2].strip()
        track = tkl.TrackReader.parseWkt(wkt, )
        track.tid = edge_id
        fusions.addTrack(track)
print ('Nombre de traces dans la collection : ', fusions.size())

for trace in fusions:
    trace.plot('m-', append=ax1)


# Conflation
conflated = conflateOnNetwork(fusions, network, threshold=50, h=30)
for segment in conflated:
    if segment is not None:
        segment.plot('c-', append=ax1)



# ===========================================================================

ax2 = plt.subplot2grid((1, 2), (0, 1))

# lire les traces raccordées envoyées
raccordees = tkl.TrackCollection()
for raccordfilename in os.listdir(raccordpath):
    with open(raccordpath + raccordfilename, 'r') as file:
        line = file.readline()
        line = file.readline()
        items = line.split(";")
        edge_id = items[0]
        wkt = items[1].strip()
        track = tkl.TrackReader.parseWkt(wkt, )
        track.tid = edge_id
        raccordees.addTrack(track)
print ('Nombre de traces raccordées : ', raccordees.size())

for trace in raccordees:
    trace.plot('b-', append=ax2)



ax1.set_xlim([949645, 949670])
ax2.set_xlim([949645, 949670])
ax1.set_ylim([6511825, 6511867])
ax2.set_ylim([6511825, 6511867])
plt.show()



