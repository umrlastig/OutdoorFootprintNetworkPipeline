# -*- coding: utf-8 -*-

import os
import sys
import math
import random
import shapely
import numpy as np
import matplotlib.pyplot as plt

import tracklib as tkl

netwokpath = '/home/md_vandamme/4_RESEAU/Ex2Z1Walk/network/reseau.csv'
fusionpath = '/home/md_vandamme/4_RESEAU/Ex2Z1Walk/geometry/'


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


collection = tkl.TrackCollection()
for fusionfilename in os.listdir(fusionpath):
    with open(fusionpath + fusionfilename, 'r') as file:
        line = file.readline()
        line = file.readline()
        items = line.split(";")
        edge_id = items[0]
        wkt = items[2].strip()
        track = tkl.TrackReader.parseWkt(wkt, )
        track.tid = edge_id
        collection.addTrack(track)
print ('Nombre de traces dans la collection : ', collection.size())


conflated = tkl.conflateOnNetwork(collection, network, threshold=50, h=30)

network.plot()

for segment in collection:
	plt.plot(segment['x'], segment['y'], 'r-', linewidth=0.3)
for segment in conflated:
	plt.plot(segment['x'], segment['y'], 'g-', linewidth=1)

plt.show()




