# -*- coding: utf-8 -*-



# import matplotlib.pyplot as plt

import tracklib as tkl
from tracklib.util.qgis import QGIS, LineStyle, PointStyle

NB_OBS_MIN    = 10
DIST_MAX_2OBS = 50
SEARCH        = 25

tracepath  = r'/home/md_vandamme/5_GPS/OV/BAUGES/walk/6736477209049897211.csv'
netwokpath = r'/home/md_vandamme/4_RESEAU/ExampleTest/network/reseau.csv'



# -----------------------------------------------------------------------------
#    Chargement de la trace

fmt = tkl.TrackFormat({'ext': 'CSV',
                       'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': -1,
                       'srid': 'ENUCoords',
                       #'time_fmt': '4Y-2M-2DT2h:2m:2s',
                       'separator': ';',
                       'header': 0,
                       'cmt': '#',
                       'verbose': False})

trace = tkl.TrackReader.readFromFile(tracepath, fmt)
print ("Size of track ", trace.size())

X = [949798, 950234, 951228, 951259, 950326, 950120, 950298, 949766, 949329, 949138, 949145, 949340, 949397, 949457, 949798]
Y = [6513065, 6513079, 6512862, 6512504, 6512529, 6512224, 6511908, 6511248, 6510989, 6511152, 6511415, 6511794, 6512337, 6513104, 6513065]

poly = tkl.Polygon(X, Y)
constraintBBox = tkl.Constraint(shape=poly,
                                mode=tkl.MODE_CROSSES,
                                type=tkl.TYPE_CUT_AND_SELECT)

collection = tkl.TrackCollection()
cpttrace = 1
for trace in tkl.TrackCollection([trace]):
    selection = constraintBBox.select(tkl.TrackCollection([trace]))
    if len(selection) <= 0:
        continue

    o1 = None
    tn = tkl.Track()
    for o2 in selection.getTrack(0):
        if o1 is not None:
            if o1.distance2DTo(o2) > DIST_MAX_2OBS:
                # on coupe la trace
                if tn.size() >= NB_OBS_MIN:
                    tn.uid = str(trace.tid) + "-" + str(cpttrace)
                    tn.tid = str(trace.tid) + "-" + str(cpttrace)
                    cpttrace += 1
                    collection.addTrack(tn)
                tn = tkl.Track([])
        tn.addObs(o2)
        o1 = o2

    # dernière trace
    if tn.size() >= NB_OBS_MIN:
        tn.uid = str(trace.tid) + "-" + str(cpttrace)
        tn.tid = str(trace.tid) + "-" + str(cpttrace)
        cpttrace += 1
        collection.addTrack(tn)


print ('Size of collection : ', collection.size())

QGIS.plotTracks(collection, type='POINT',
                style=PointStyle.simpleSquareBlue,
                title='Points découpés')
QGIS.plotTracks(collection, type='LINE',
                style=LineStyle.simpleBlue,
                title='Lignes découpées')


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


# -----------------------------------------------------------------------------
#     Map matching

si = tkl.SpatialIndex(network, verbose=False)
network.spatial_index = si
network.prepare()

print ('Launching Map-matching')
tkl.mapOnNetwork(collection, network, search_radius=SEARCH, debug=False)
print ('Map-matching ended')



# -----------------------------------------------------------------------------
#       Affichage dans QGIS des résultats


layer = QgsVectorLayer("Point?crs=epsg:2154", "MM", "memory")
pr = layer.dataProvider()
pr.addAttributes([QgsField("idtrace", QVariant.String)])
pr.addAttributes([QgsField("idpoint", QVariant.Int)])
pr.addAttributes([QgsField("xp", QVariant.Double)])
pr.addAttributes([QgsField("yp", QVariant.Double)])
pr.addAttributes([QgsField("xm", QVariant.Double)])
pr.addAttributes([QgsField("ym", QVariant.Double)])
pr.addAttributes([QgsField("type", QVariant.String)])
layer.updateFields()

layerLinkMM = QgsVectorLayer("LineString?crs=epsg:2154", "Link MM", "memory")
prMM = layerLinkMM.dataProvider()
prMM.addAttributes([QgsField("idtrace", QVariant.String)])
prMM.addAttributes([QgsField("idedge", QVariant.String)])
pr.addAttributes([QgsField("distsource", QVariant.Double)])
pr.addAttributes([QgsField("disttarget", QVariant.Double)])
layerLinkMM.updateFields()


for i in range(collection.size()):
    track = collection.getTrack(i)
    pkid = track.uid
    # print (pkid)

    for j in range(track.size()):

        obs = track.getObs(j)
        x = float(obs.position.getX())
        y = float(obs.position.getY())
        pt1 = QgsPointXY(x, y)
        g1 = QgsGeometry.fromPointXY(pt1)

        ide = str(track["hmm_inference", j][1])
        ds = float(track["hmm_inference", j][2])
        dt = float(track["hmm_inference", j][3])

        e1 = track["hmm_inference", j][1]
        e = network.EDGES[network.getEdgeId(e1)]

        if ide != "-1" and ds > 0.01 and dt > 0.01:

            xmm = track["hmm_inference", j][0].getX()
            ymm = track["hmm_inference", j][0].getY()
            pt2 = QgsPointXY(xmm, ymm)
            g2 = QgsGeometry.fromPointXY(pt2)

            attrs1 = [str(pkid), j, x, y, float(xmm), float(ymm), 'ARC']
            fet = QgsFeature()
            fet.setAttributes(attrs1)
            fet.setGeometry(g2)
            pr.addFeature(fet)

            line = QgsGeometry.fromPolylineXY([pt1, pt2])
            fet = QgsFeature()
            fet.setGeometry(line)
            attrs1 = [str(pkid), str(ide), ds, dt]
            fet.setAttributes(attrs1)
            prMM.addFeature(fet)


        elif abs(ds) < 0.01:
            # node = network.getEdge(ide).source
            node = e.source
            xmm = node.coord.getX()
            ymm = node.coord.getY()
            pt2 = QgsPointXY(xmm, ymm)
            g2 = QgsGeometry.fromPointXY(pt2)

            attrs1 = [str(pkid), j, x, y, float(xmm), float(ymm), 'NOEUD']
            fet = QgsFeature()
            fet.setAttributes(attrs1)
            fet.setGeometry(g2)
            pr.addFeature(fet)

            line = QgsGeometry.fromPolylineXY([pt1, pt2])
            fet = QgsFeature()
            fet.setGeometry(line)
            attrs1 = [str(pkid), str(ide), ds, dt]
            fet.setAttributes(attrs1)
            prMM.addFeature(fet)

        elif abs(dt) < 0.01:
            # node = network.getEdge(ide).target
            node = e.target
            xmm = node.coord.getX()
            ymm = node.coord.getY()
            pt2 = QgsPointXY(xmm, ymm)
            g2 = QgsGeometry.fromPointXY(pt2)

            attrs1 = [str(pkid), j, x, y, float(xmm), float(ymm), 'NOEUD']
            fet = QgsFeature()
            fet.setAttributes(attrs1)
            fet.setGeometry(g2)
            pr.addFeature(fet)

            line = QgsGeometry.fromPolylineXY([pt1, pt2])
            fet = QgsFeature()
            fet.setGeometry(line)
            attrs1 = [str(pkid), str(ide), ds, dt]
            fet.setAttributes(attrs1)
            prMM.addFeature(fet)

        else:
            # pas de MM

            attrs1 = [str(pkid), j, x, y, -1, -1, 'NOMM']
            fet = QgsFeature()
            fet.setAttributes(attrs1)
            fet.setGeometry(g1)
            pr.addFeature(fet)


layer.updateExtents()
QgsProject.instance().addMapLayer(layer)

layerLinkMM.updateExtents()
QgsProject.instance().addMapLayer(layerLinkMM)


