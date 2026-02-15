# -*- coding: utf-8 -*-

'''
    Recalage des points sur le réseau
'''

import sys
import csv
csv.field_size_limit(sys.maxsize)

import tracklib as tkl

from . import plotMM

from tracklib.util.qgis import QGIS, LineStyle, PointStyle
from PyQt5.QtGui import QColor

try:
    from qgis.PyQt.QtCore import QVariant
    from qgis.core import QgsStyle, QgsColorRampShader, QgsColorRampShader, QgsRasterShader
    from qgis.core import QgsSingleBandPseudoColorRenderer, QgsRasterLayer, QgsProject
    from qgis.core import QgsCoordinateReferenceSystem, QgsVectorLayer, QgsFeatureRequest
    from qgis.core import QgsField, QgsGeometry, QgsFeature, QgsVectorFileWriter
    from qgis.core import QgsMarkerSymbol, QgsPointXY
    from PyQt5.QtGui import QColor
    import processing
    from qgis.core import edit
except ImportError:
    print ('Code running in a no qgis environment')




def bonneTrace(tn, edge, NB_OBS_MIN, SEARCH):
        '''
        Fonction utilitaire.
        Une trace est gardée pour la fusion si son point de départ est "proche" 
        d'un noeud de l'arc et son point d'arrivée est "proche" de l'autre noeud de l'arc.
        '''

        morceaux = tkl.TrackCollection()

        if tn.size() >= NB_OBS_MIN:

            p1 = tn.getFirstObs().position
            p2 = tn.getLastObs().position

            s = edge.source.coord
            t = edge.target.coord

            if edge.geom.length() < 2*SEARCH:
                if p1.distance2DTo(s) < SEARCH/2 and p2.distance2DTo(t) < SEARCH/2:
                    morceaux.addTrack(tn)
                if p1.distance2DTo(t) < SEARCH/2 and p2.distance2DTo(s) < SEARCH/2:
                    morceaux.addTrack(tn.reverse())
            else:

                if p1.distance2DTo(s) < SEARCH:
                    reverse = False
                    atteint = False
                    dd = 0
                    for idx, o in enumerate(tn):
                        if o.position.distance2DTo(t) < SEARCH:
                            atteint = True
                        if atteint and o.position.distance2DTo(t) > SEARCH:
                            # la deuxième partie de la trace est sortie
                            t1 = tn.extract(dd, idx-1)
                            dd = idx
                            morceaux.addTrack(t1)
                            t = s
                            s = o.position
                            atteint = False
                            reverse = True
                    if atteint:
                        t1 = tn.extract(dd, idx)
                        if reverse:
                            morceaux.addTrack(t1.reverse())
                        else:
                            morceaux.addTrack(t1)


                if p2.distance2DTo(s) < SEARCH:
                    tnr = tn.reverse()
                    reverse = False
                    atteint = False
                    dd = 0
                    for idx, o in enumerate(tnr):
                        if o.position.distance2DTo(t) < SEARCH:
                            atteint = True
                        if atteint and o.position.distance2DTo(t) > SEARCH:
                            # la deuxième partie de la trace est sortie
                            t1 = tn.extract(dd, idx-1)
                            dd = idx
                            morceaux.addTrack(t1)
                            t = s
                            s = o.position
                            atteint = False
                            reverse = True
                    if atteint:
                        t1 = tnr.extract(dd, idx)
                        if reverse:
                            morceaux.addTrack(t1.reverse())
                        else:
                            morceaux.addTrack(t1)

        return morceaux





def mapmatch(RESPATH, SEARCH, DIST_MAX_2OBS, NB_OBS_MIN):

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
    
    netwokpath = RESPATH + 'network/reseau.csv'
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
    tracespath = RESPATH + '/resample/'
    collection2 = tkl.TrackReader.readFromFile(tracespath, fmt)
    print ('Nombre de traces:', collection2.size())

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
    
        # if cptId > 30:
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


    # =============================================================================
    #     Stats Map-matching
    #

    for i in range(collection.size()):
        track = collection.getTrack(i)
        pkid = track.tid
    
        for j in range(track.size()):
            pb  = track[j].position
            # mm  = track["hmm_inference", j][0]

            ds = float(track["hmm_inference", j][2])
            dt = float(track["hmm_inference", j][3])

            idxedge = track["hmm_inference", j][1]
            edgeid = network.getEdgeId(idxedge)
            e = network.EDGES[edgeid]
    
            if idxedge != -1 and ds > 0.01 and dt > 0.01:
                if edgeid not in MM:
                    MM[edgeid] = {}
                if pkid not in MM[edgeid].keys():
                    MM[edgeid][pkid] = []
                MM[edgeid][pkid].append((j,pb))
            elif abs(ds) < 0.01:
                idnode = e.source.id
                edgesid = network.getIncidentEdges(idnode)
                for eid in edgesid:
                    if eid not in MM:
                        MM[eid] = {}
                    if pkid not in MM[eid].keys():
                        MM[eid][pkid] = []
                    MM[eid][pkid].append((j,pb))
            elif abs(dt) < 0.01:
                idnode = e.target.id
                edgesid = network.getIncidentEdges(idnode)
                for eid in edgesid:
                    if eid not in MM:
                        MM[eid] = {}
                    if pkid not in MM[eid].keys():
                        MM[eid][pkid] = []
                    MM[eid][pkid].append((j,pb))
    
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
    
    plotMM(collection, network)


    # =============================================================================
    #  On prépare les traces pour la fusion:
    #     - créer des morceaux
    #     - toutes les traces dans le même sens
    # on enregistre le MM dans un fichier CSV
    
    mmpath = RESPATH + 'mapmatch/resultmm.csv'

    NBPasBonne = 0

    f = open(mmpath,'w')
    f.write("EDGE_ID;TRACK_ID;WKT\n")

    for edgeid, tobstrack in MM.items():
        e = network.EDGES[edgeid]

        for trackid, tobs in tobstrack.items():
            points_sorted = sorted(tobs, key=lambda x: x[0])
    
            tn = tkl.Track()
            p1 = None
            for p in points_sorted:
                p2 = p[1]
                if p1 is not None:
                    if p2.distance2DTo(p1)> DIST_MAX_2OBS:
                        # on coupe la trace pour créer un nouveau morceau
                        cb = bonneTrace(tn, e, NB_OBS_MIN, SEARCH)
                        for tb in cb:
                            f.write(str(edgeid) + ";" + str(trackid) + ";" + tb.toWKT() + "\n")
                        if cb.size() <= 0:
                            NBPasBonne += 1
                        tn = tkl.Track()
                tn.addObs(tkl.Obs(p2, tkl.ObsTime()))
                p1 = p2

            # dernier morceau de trace
            cb = bonneTrace(tn, e, NB_OBS_MIN, SEARCH)
            for tb in cb:
                f.write(str(edgeid) + ";" + str(trackid) + ";" + tn.toWKT() + "\n")
            if cb.size() <= 0:
                NBPasBonne += 1

    f.close()


    txtpath = r"file:///" + mmpath + "?delimiter=;&wktField=WKT&crs=EPSG:2154"
    layerTracksForFusion = QgsVectorLayer(txtpath, "tracks for fusion", "delimitedtext")
    QgsProject.instance().addMapLayer(layerTracksForFusion)

    print ('Nombre de traces rejetées : ', NBPasBonne)
    
    # =============================================================================
    
    print ("Fin du recalage.")
    print ("END SCRIPT 5.")

