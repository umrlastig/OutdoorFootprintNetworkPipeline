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


# Map matching
SEARCH = 25

netwokpath          = r'/home/md_vandamme/4_RESEAU/ExampleTest/network/reseau.csv'
resampledtracespath = r'/home/md_vandamme/4_RESEAU/ExampleTest/resample/'



# =============================================================================

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


layerEdges = QgsVectorLayer("LineString?crs=EPSG:2154", "TRONCONS OF", "memory")
pr1 = layerEdges.dataProvider()
pr1.addAttributes([QgsField("idedge", QVariant.String)])
pr1.addAttributes([QgsField("source", QVariant.Int)])
pr1.addAttributes([QgsField("target", QVariant.Int)])
pr1.addAttributes([QgsField("orientation", QVariant.Int)])
pr1.addAttributes([QgsField("weight", QVariant.Double)])
pr1.addAttributes([QgsField("mm", QVariant.Int)])
layerEdges.updateFields()

layerNodes = QgsVectorLayer("Point?crs=EPSG:2154", "NOEUDS OF", "memory")
pr2 = layerNodes.dataProvider()
pr2.addAttributes([QgsField("idnode", QVariant.String)])
layerNodes.updateFields()

L = list(network.EDGES.items())
for i in range(len(L)):
    edge = L[i][1]
    POINTS = []
    for j in range(edge.geom.size()):
        pt = QgsPointXY(edge.geom.getX()[j], edge.geom.getY()[j])
        POINTS.append(pt)
    fet = QgsFeature()
    fet.setAttributes([str(edge.id), int(edge.source.id), int(edge.target.id),
                           edge.orientation, edge.weight, 0])
    fet.setGeometry(QgsGeometry.fromPolylineXY(POINTS))
    pr1.addFeatures([fet])
layerEdges.updateExtents()
LineStyle.topoRoad(layerEdges)

L = list(network.NODES.items())
for i in range(len(L)):
    node = L[i][1]
    pt = QgsPointXY(node.coord.getX(), node.coord.getY())
    fet = QgsFeature()
    fet.setAttributes([str(node.id)])
    fet.setGeometry(QgsGeometry.fromPointXY(pt))
    pr2.addFeatures([fet])
layerNodes.updateExtents()
PointStyle.simpleBlack(layerNodes)

QgsProject.instance().addMapLayer(layerEdges)
QgsProject.instance().addMapLayer(layerNodes)


# =============================================================================
fmt = tkl.TrackFormat({'ext': 'CSV',
                       'srid': 'ENU',
                       'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                       'separator': ';',
                       'header': 1})
collection2 = tkl.TrackReader.readFromFile(resampledtracespath, fmt)

layer = QgsVectorLayer("Point?crs=EPSG:2154", "Traces points", "memory")
pr = layer.dataProvider()
pr.addAttributes([QgsField("idtrace", QVariant.String)])
pr.addAttributes([QgsField("idpoint", QVariant.Int)])
layer.updateFields()

cptId = 1
collection = tkl.TrackCollection()
for trace in collection2:
    trace.uid = cptId
    trace.tid = cptId
    cptId += 1

    for j in range(trace.size()):
        obs = trace.getObs(j)
        X = float(obs.position.getX())
        Y = float(obs.position.getY())
        pt = QgsPointXY(X, Y)
        gPoint = QgsGeometry.fromPointXY(pt)
        
        attrs = [str(cpt), j]
        fet = QgsFeature()
        fet.setAttributes(attrs)
        fet.setGeometry(gPoint)
        pr.addFeature(fet)

    #if trace.size() > 10:
    collection.addTrack(trace)

layer.updateExtents()
symbol = QgsMarkerSymbol.createSimple({
    'name': 'square', 
    'color': QColor.fromRgb(157, 193, 131),
    'size':'1.4'})
layer.renderer().setSymbol(symbol)
QgsProject.instance().addMapLayer(layer)



# =============================================================================
#     Map-matching
#

def plotMM(collection):

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

            elif ds < 0.01:
                node = network.getEdge(ide).source
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

            elif dt < 0.01:
                node = network.getEdge(ide).target
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


    layer.updateExtents()
    QgsProject.instance().addMapLayer(layer)

    layerLinkMM.updateExtents()
    QgsProject.instance().addMapLayer(layerLinkMM)


MM = {}
MMN = {}

field = layerEdges.fields().lookupField("mm")

si = tkl.SpatialIndex(network, verbose=False)
network.spatial_index = si

# computes all distances between pairs of nodes
network.prepare()


# Map track on network
print ('Launching Map-matching')
tkl.mapOnNetwork(collection, network, search_radius=SEARCH, debug=False)
print ('Map-matching ended')

for i in range(collection.size()):
    track = collection.getTrack(i)
    pkid = track.uid

    for j in range(track.size()):
        pb  = track[j].position
        # mm  = track["hmm_inference", j][0]
        ide = str(track["hmm_inference", j][1])
        ds = float(track["hmm_inference", j][2])
        dt = float(track["hmm_inference", j][3])
        if ide != "-1" and ds > 0.01 and dt > 0.01:
            if ide not in MM:
                MM[ide] = {}
            if pkid not in MM[ide].keys():
                MM[ide][pkid] = []
            MM[ide][pkid].append(pb)
        elif ds < 0.01:
            idnode = network.getEdge(ide).source.id
            if idnode not in MMN:
                MMN[idnode] = {}
            if pkid not in MMN[idnode].keys():
                MMN[idnode][pkid] = []
            MMN[idnode][pkid].append(pb)
        elif dt < 0.01:
            idnode = network.getEdge(ide).target.id
            if idnode not in MMN:
                MMN[idnode] = {}
            if pkid not in MMN[idnode].keys():
                MMN[idnode][pkid] = []
            MMN[idnode][pkid].append(pb)


print ('Stats computing ended')

with edit(layerEdges):
    for edid in network.EDGES.keys():
        if edid not in MM:
            layerEdges.selectByExpression(" idedge = '" + edid +"'")
            for f in layerEdges.getSelectedFeatures():
                feature_id = f.id()
                layerEdges.changeAttributeValue(feature_id, field, 1)
                break
layerEdges.setSubsetString("")

plotMM(collection)


# =============================================================================
#     Fusion
#

'''
cellsize = min(network.spatial_index.csize, network.spatial_index.lsize)
newunit = math.ceil(25 / cellsize)

# Aggregation with DTW distance

layer = QgsVectorLayer("Point?crs=epsg:2154", "PourFusion", "memory")
pr = layer.dataProvider()
pr.addAttributes([QgsField("idedge", QVariant.String)])
pr.addAttributes([QgsField("idtrace", QVariant.String)])
pr.addAttributes([QgsField("idobs", QVariant.Int)])
layer.updateFields()

N = len(MM)
print ('N = ', N)
fusions = tkl.TrackCollection()
for edgeid in MM:
    #if edgeid not in ['701', '703']:
    #    continue
    #print (edgeid)

    traces = MM[edgeid]

    TRACES = []
    for traceid in traces:
        t = tkl.Track()
        coords = traces[traceid]
        for (k, p) in enumerate(coords):
            t.addObs(tkl.Obs(p))

            fet = QgsFeature()
            fet.setAttributes([edgeid, traceid, k])
            x = float(p.getX())
            y = float(p.getY())
            pt1 = QgsPointXY(x, y)
            fet.setGeometry(QgsGeometry.fromPointXY(pt1))
            fet.setAttributes([str(edgeid), traceid, k])
            pr.addFeature(fet)

        if t.size() > 2:
            TRACES.append(t)

    candidatsMultiSens = tkl.TrackCollection(TRACES)
    if candidatsMultiSens.size() <= 0:
        continue

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
        if NB <= 20:
            candidats20 = candidats
        else:
            candidats20 = candidats.randNTracks(20)

        centralDTW = tkl.fusion(candidats20,
                             master=tkl.MODE_MASTER_MEDIAN_LEN,
                             dim=2,
                             mode=tkl.MODE_MATCHING_DTW,
                             p=2,
                             represent_method=tkl.MODE_REP_BARYCENTRE,
                             agg_method=tkl.MODE_AGG_MEDIAN,
                             constraint=False,
                             verbose=False,
                             iter_max=25)
        # print (candidats20.size(), ' fusions', edgeid)
        fusions.addTrack(centralDTW)
    elif candidats.size() == 1:
        centralDTW = candidats.getTrack(0)
        # print ('une fusion', edgeid)
        fusions.addTrack(centralDTW)
    #else:
    #    print ('Pas de fusion')

    N = N - 1
    if N%10 == 0:
        print ('N=', N)


layer.updateExtents()
QgsProject.instance().addMapLayer(layer)
print ('Fin fusion')

print ('Number of aggregations: ', fusions.size())

QGIS.plotTracks(fusions, type='LINE', style=LineStyle.simpleVert1, title='Fusions')
'''



# =============================================================================


print ("Fin de la fusion.")


print ("END SCRIPT 5.")

