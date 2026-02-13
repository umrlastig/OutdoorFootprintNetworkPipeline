# -*- coding: utf-8 -*-

'''
    Recalage des points sur le réseau
'''

import sys
import csv
csv.field_size_limit(sys.maxsize)


import tracklib as tkl

from tracklib.util.qgis import QGIS, LineStyle, PointStyle
from PyQt5.QtGui import QColor


# Map matching
SEARCH = 25

# Préparation à la fusion
NB_OBS_MIN    = 10
DIST_MAX_2OBS = 50

netwokpath          = r'/home/md_vandamme/4_RESEAU/ExampleTest/network/reseau.csv'
#resampledtracespath = r'/home/md_vandamme/4_RESEAU/ExampleTest/resample/'
tracespath          = r'/home/md_vandamme/4_RESEAU/ExampleTest/decoup/'
mmpath              = r'/home/md_vandamme/4_RESEAU/ExampleTest/mapmatch/resultmm.csv'

# =============================================================================
#    Lecture du réseau
#
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
#   Lecture des traces découpées et ré-échantillonnées.
#
fmt = tkl.TrackFormat({'ext': 'CSV',
                       'srid': 'ENU',
                       'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                       'time_fmt': '2D/2M/4Y 2h:2m:2s',
                       'separator': ';',
                       'header': 0,
                       'cmt': '#',
                       'read_all': True})
collection2 = tkl.TrackReader.readFromFile(tracespath, fmt)

layer = QgsVectorLayer("Point?crs=EPSG:2154", "Traces points", "memory")
pr = layer.dataProvider()
pr.addAttributes([QgsField("idtrace", QVariant.String)])
pr.addAttributes([QgsField("idpoint", QVariant.Int)])
layer.updateFields()

cptId = 1
collection = tkl.TrackCollection()
for trace in collection2:

    # print (trace.uid, trace.tid)

    trace.uid = cptId
    trace.tid = cptId
    cptId += 1

    #if cptId > 30:
    #    break

    for j in range(trace.size()):
        obs = trace.getObs(j)
        X = float(obs.position.getX())
        Y = float(obs.position.getY())
        pt = QgsPointXY(X, Y)
        gPoint = QgsGeometry.fromPointXY(pt)
        
        attrs = [str(trace.tid), j]
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
        pkid = track.tid
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

    # -------------------------------------------------------------------------

    # QgsRendererCategory
    symbolArc = QgsSymbol.defaultSymbol(layer.geometryType())
    symbolArc.setColor(QColor.fromRgb(148,240,96))
    categoryArc = QgsRendererCategory("ARC", symbolArc, "ARC")

    symbolNoeud = QgsSymbol.defaultSymbol(layer.geometryType())
    symbolNoeud.setColor(QColor.fromRgb(60,186,250))
    categoryNoeud = QgsRendererCategory("NOEUD", symbolNoeud, "NOEUD")

    symbolNon = QgsSymbol.defaultSymbol(layer.geometryType())
    symbolNon.setColor(QColor.fromRgb(235,70,124))
    categoryNon = QgsRendererCategory("NOMM", symbolNon, "NOMM")


    # On definit une liste pour y stocker 2 QgsRendererCategory
    categories = []
    categories.append(categoryNon)
    categories.append(categoryNoeud)
    categories.append(categoryArc)

    # On construit une expression pour appliquer les categories
    expression = 'type' # field name
    renderer = QgsCategorizedSymbolRenderer(expression, categories)
    layer.setRenderer(renderer)


    # -------------------------------------------------------------------------


MM = {}   #  [ide][pkid] : liste des observations

field = layerEdges.fields().lookupField("mm")

si = tkl.SpatialIndex(network, verbose=False)
network.spatial_index = si


# Computes all distances between pairs of nodes
network.prepare()


# Map track on network
print ('Launching Map-matching')
tkl.mapOnNetwork(collection, network, search_radius=SEARCH, debug=False)
print ('Map-matching ended')

for i in range(collection.size()):
    track = collection.getTrack(i)
    pkid = track.tid

    for j in range(track.size()):
        pb  = track[j].position
        # mm  = track["hmm_inference", j][0]
        ide = str(track["hmm_inference", j][1])
        ds = float(track["hmm_inference", j][2])
        dt = float(track["hmm_inference", j][3])

        e1 = track["hmm_inference", j][1]
        e = network.EDGES[network.getEdgeId(e1)]

        if ide != "-1" and ds > 0.01 and dt > 0.01:
            if ide not in MM:
                MM[ide] = {}
            if pkid not in MM[ide].keys():
                MM[ide][pkid] = []
            MM[ide][pkid].append((j,pb))
        elif abs(ds) < 0.01:
            idnode = e.source.id
            edgesid = network.getIncidentEdges(idnode)
            for edgeid in edgesid:
                if edgeid not in MM:
                    MM[edgeid] = {}
                if pkid not in MM[edgeid].keys():
                    MM[edgeid][pkid] = []
                MM[edgeid][pkid].append((j,pb))
        elif abs(dt) < 0.01:
            idnode = e.target.id
            edgesid = network.getIncidentEdges(idnode)
            for edgeid in edgesid:
                if edgeid not in MM:
                    MM[edgeid] = {}
                if pkid not in MM[edgeid].keys():
                    MM[edgeid][pkid] = []
                MM[edgeid][pkid].append((j,pb))

print ('Stats computing ended.')

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
#  On prépare les traces pour la fusion:
#     - créer des morceaux
#     - toutes les traces dans le même sens
# on enregistre le MM dans un fichier CSV


NB_OBS_MIN    = 10
DIST_MAX_2OBS = 50

f = open(mmpath,'w')
f.write("EDGE_ID;TRACK_ID;WKT\n")
for edgeid, tobstrack in MM.items():
    for trackid, tobs in tobstrack.items():
        points_sorted = sorted(tobs, key=lambda x: x[0])

        txt = "LINESTRING("
        cpt = 0
        pold = None
        for p in points_sorted:
            cpt += 1
            if pold != None:
                if p[1].distance2DTo(pold)> DIST_MAX_2OBS:
                    # on coupe la trace pour créer un nouveau morceau
                    if cpt >= NB_OBS_MIN:
                        if len(txt) > 1:
                            txt = txt[0:len(txt)-2] + ")"
                            f.write(str(edgeid) + ";" + str(trackid) + ";" + txt + "\n")
                    txt = "LINESTRING("
                    cpt = 0

            pt = p[1]
            txt += str(pt.getX()) + " " + str(pt.getY()) + ","
            pold = pt

        # dernier morceau de trace
        if cpt >= NB_OBS_MIN:
            if len(txt) > 1:
                txt = txt[0:len(txt)-2] + ")"
                f.write(str(edgeid) + ";" + str(trackid) + ";" + txt + "\n")

f.close()

txtpath = r"file:///" + mmpath + "?delimiter=;&wktField=WKT&crs=EPSG:2154"
layerTracksForFusion = QgsVectorLayer(txtpath, "tracks for fusion", "delimitedtext")
QgsProject.instance().addMapLayer(layerTracksForFusion)


# =============================================================================


print ("Fin du recalage.")
print ("END SCRIPT 5.")

