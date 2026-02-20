# -*- coding: utf-8 -*-

import sys
import csv
csv.field_size_limit(sys.maxsize)

import tracklib as tkl


RESPATH = r'/home/md_vandamme/4_RESEAU/Ex2Z1Walk/'
respath = RESPATH + 'image/'


# =============================================================================
#       Chargement des traces GPS
#  Ici elles sont mises dans un fichier CSV dont la géométrie de la trace est
#  dans le format WKT
'''
fmt = tkl.TrackFormat({'ext': 'WKT',
                       'srid': 'ENU',
                       'id_wkt': 0,
                       'separator': ';',
                       'header': 1})

z2path = r'/home/md_vandamme/4_RESEAU/V1/zone3/data/zone3-walk.csv'
collection = tkl.TrackReader.readFromFile(z2path, fmt)

cpt = 1
for trace in collection:
    trace.uid = cpt
    trace.tid = cpt
    cpt += 1
print ('Number of tracks in zone1: ' + str(collection.size()))  # 705
'''

fmt = tkl.TrackFormat({'ext': 'CSV',
                       'srid': 'ENU',
                       'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                       'separator': ';',
                       'header': 1,
                       'read_all': True})

resampledtracespath = RESPATH + 'resample1/'
collection = tkl.TrackReader.readFromFile(resampledtracespath, fmt)
for trace in collection:
    trace.uid = trace.getObsAnalyticalFeature('user_id', 0)
    trace.tid = trace.getObsAnalyticalFeature('track_id', 0)
print ('Number of tracks : ', collection.size()) # 1171



G1_SIZE = 2

af_algos = ['uid']
cell_operators = [tkl.co_count_distinct]

marge = 0
resolutionG1 = (G1_SIZE, G1_SIZE)
bbox = collection.bbox()

rasterG1 = tkl.summarize(collection, af_algos, cell_operators, resolutionG1, marge,
                   align=tkl.BBOX_ALIGN_CENTER)
grilleG1 = rasterG1.getAFMap('uid#co_count_distinct')
for i in range(grilleG1.raster.nrow):
    for j in range(grilleG1.raster.ncol):
        grilleG1.grid[i][j] = grilleG1.grid[i][j] / (G1_SIZE*G1_SIZE)

pathres = RESPATH + 'image/zone3_G1_1.asc'
tkl.RasterWriter.writeMapToAscFile(pathres, grilleG1)


