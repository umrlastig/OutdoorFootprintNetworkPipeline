# -*- coding: utf-8 -*-

'''
import matplotlib.pyplot as plt
import tracklib as tkl
from tracklib.util.qgis import QGIS, LineStyle, PointStyle

RESAMPLE_SIZE = 1
G1_SIZE = 2
G2_SIZE = 50


X = [945878, 956330, 955879, 954402, 952511, 950389, 948774, 945857, 945878]
Y = [6516870, 6516805, 6508417, 6506849, 6506503, 6505649, 6504150, 6503762, 6516870]

poly = tkl.Polygon(X, Y)
constraintBBox = tkl.Constraint(shape=poly, mode=tkl.MODE_CROSSES,
                            type=tkl.TYPE_CUT_AND_SELECT)


fmt = tkl.TrackFormat({'ext': 'CSV',
                       'srid': 'ENU',
                       'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                       'time_fmt': '2D/2M/4Y 2h:2m:2s',
                       'separator': ';',
                       'header': 0,
                       'cmt': '#',
                       'read_all': True})

# z1path = r'/home/md_vandamme/3_IntForOut/DATA/OV/BAUGES/zone1/'
z2path = r'/home/md_vandamme/5_GPS/OV/BAUGES/walk/'
collection2 = tkl.TrackReader.readFromFile(z2path, fmt)

collection = tkl.TrackCollection()
for trace in collection2:
    selection = constraintBBox.select(tkl.TrackCollection([trace]))
    if len(selection) <= 0:
        continue

    o1 = None
    tn = tkl.Track()
    for o2 in selection.getTrack(0):
        if o1 is not None:
            if o1.distance2DTo(o2) > 50:
                # on coupe la trace
                if tn.size() >= 10:
                    collection.addTrack(tn)
                tn = tkl.Track()
        tn.addObs(o2)
        o1 = o2
    # dernière trace
    if tn.size() >= 10:
        collection.addTrack(tn)


for trace in collection:
    trace.uid = trace.tid
    trace.resample(RESAMPLE_SIZE, tkl.MODE_SPATIAL)
print ('Number of tracks in zone1: ' + str(collection.size()))

QGIS.plotTracks(collectionZone1, type='LINE',
                style=LineStyle.simpleBlue, title='Zone2-walk')
'''










