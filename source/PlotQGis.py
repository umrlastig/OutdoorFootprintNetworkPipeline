# -*- coding: utf-8 -*-

from tracklib.util.qgis import QGIS, LineStyle, PointStyle

try:
    from qgis.PyQt.QtCore import QVariant
    from qgis.core import QgsStyle, QgsColorRampShader, QgsColorRampShader, QgsRasterShader
    from qgis.core import QgsSingleBandPseudoColorRenderer, QgsRasterLayer, QgsProject
    from qgis.core import QgsCoordinateReferenceSystem, QgsVectorLayer, QgsField
    from qgis.core import  QgsPointXY, QgsFeature, QgsGeometry
    from qgis.core import QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer
    from PyQt5.QtGui import QColor
except ImportError:
    print ('Code running in a no qgis environment')



def styleTurbo(layerGrid):
    style = QgsStyle().defaultStyle()
    ramp = style.colorRamp("Turbo")

    color_ramp = QgsColorRampShader()
    color_ramp.setColorRampType(QgsColorRampShader.Interpolated)

    provider = layerGrid.dataProvider()
    stats = provider.bandStatistics(1)
    vmin, vmax = 0, stats.maximumValue

    nb_classes = 256
    items = []
    for i in range(nb_classes):
        value = float(vmin) + (vmax - vmin) * float(i) / (nb_classes - 1)
        color = ramp.color(i / (nb_classes - 1))
        items.append(QgsColorRampShader.ColorRampItem(value, color))
    color_ramp.setColorRampItemList(items)

    shader = QgsRasterShader()
    shader.setRasterShaderFunction(color_ramp)

    renderer = QgsSingleBandPseudoColorRenderer(provider, 1, shader)
    renderer.setClassificationMin(0)
    renderer.setClassificationMax(stats.maximumValue)

    layerGrid.setRenderer(renderer)


def plotRaster(pathres, title, style=None):

    layerGrid = QgsRasterLayer(pathres, title, "gdal")
    layerGrid.setCrs(QgsCoordinateReferenceSystem("EPSG:2154"))
    QgsProject.instance().addMapLayer(layerGrid)

    if style is not None and style == 'Turbo':
        styleTurbo(layerGrid)
        layerGrid.triggerRepaint()



def plotNetwork(network, edgeStyle='topoRoad'):
    """
    Plot a network, edges and nodes
    """

    if network.getSRID() == 'Geo':
        crs = 'crs=EPSG:4326'
    else:
        crs = 'crs=EPSG:2154'
        
    layerEdges = QgsVectorLayer("LineString?" + crs, "Edges", "memory")
    pr1 = layerEdges.dataProvider()
    pr1.addAttributes([QgsField("idedge", QVariant.String)])
    pr1.addAttributes([QgsField("source", QVariant.Int)])
    pr1.addAttributes([QgsField("target", QVariant.Int)])
    pr1.addAttributes([QgsField("orientation", QVariant.Int)])
    pr1.addAttributes([QgsField("weight", QVariant.Double)])
    layerEdges.updateFields()
    
    layerNodes = QgsVectorLayer("Point?" + crs, "Nodes", "memory")
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
                               edge.orientation, edge.weight])
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

    return (layerEdges, layerNodes)



def plotMM(collection, network):

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

            ds = float(track["hmm_inference", j][2])
            dt = float(track["hmm_inference", j][3])

            idxedge = track["hmm_inference", j][1]
            edgeid = network.getEdgeId(idxedge)
            e = network.EDGES[edgeid]

            if idxedge != -1 and ds > 0.01 and dt > 0.01:

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
                attrs1 = [str(pkid), str(edgeid), ds, dt]
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
                attrs1 = [str(pkid), str(edgeid), ds, dt]
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
                attrs1 = [str(pkid), str(edgeid), ds, dt]
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



