# -*- coding: utf-8 -*-


import tracklib as tkl
from tracklib.util.qgis import QGIS, LineStyle, PointStyle

RESPATH = r'/home/md_vandamme/4_RESEAU/Ex2Z1Walk/'

fmt = tkl.TrackFormat({'ext': 'CSV',
                       'srid': 'ENU',
                       'id_E': 1, 'id_N': 0, 'id_U': 3, 'id_T': 2,
                       'time_fmt': '2D/2M/4Y 2h:2m:2s',
                       'separator': ';',
                       'header': 0,
                       'cmt': '#',
                       'read_all': True})
collection = tkl.TrackReader.readFromFile(RESPATH + "/resample_fusion/", fmt)
# print (collection.size())


for trace in collection:
    num = trace.getObsAnalyticalFeature('num', 0)
    track_id = trace.getObsAnalyticalFeature('track_id', 0)
    user_id = trace.getObsAnalyticalFeature('user_id', 0)
    version = trace.getObsAnalyticalFeature('version', 0)

    trace.uid = user_id
    trace.tid = str(num) + '-' + version


QGIS.plotTracks(collection, type='LINE',
                style=LineStyle.simpleBlue,
                title='Resampled lines (5m)', AF=True)

QGIS.plotTracks(collection, type='POINT',
                style=PointStyle.simpleSquareBlue,
                title='Resampled points (5m)', AF=True)