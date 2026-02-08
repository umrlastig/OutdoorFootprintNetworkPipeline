# -*- coding: utf-8 -*-

'''
        TOPOLOGIE DU SQUELETTE
'''


import tracklib as tkl
from geonetlib.toolkit import createNetwork, filtreNoeudSimple, deleteSmallEdge
from geonetlib.toolkit import removeDuplicateGeometries

from tracklib.util.qgis import QGIS, LineStyle, PointStyle


# Pour la construction du réseau
tolerance = 0.1    # 0.05
seuil_doublon = 0.1

# Longueur des petits arcs à supprimer
DIST_MIN_ARC = 30     # 20


squelettepath = r'/home/md_vandamme/4_RESEAU/ExampleTest/densite/squelette.shp'
netwokpath    = r'/home/md_vandamme/4_RESEAU/ExampleTest/network/reseau.csv'




# =============================================================================


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


# =============================================================================
#          CHARGEMENT DU SQUELETTE

layerSquelette = QgsVectorLayer(squelettepath, "Squelette", "ogr")
# QgsProject.instance().addMapLayer(layerSquelette)


collection = tkl.TrackCollection()
for feat in layerSquelette.getFeatures():
    parts = feat.geometry().asGeometryCollection()
    for part in parts:
        track = tkl.TrackReader().parseWkt(part.asWkt())
        if track.length() < tolerance/2:
            continue

        collection.addTrack(track)

print ('Nb lignes : ', collection.size())
print ('Fin chargement des données 1/5.')


# =============================================================================
#             CONSTRUCTION RESEAU
#
tkl.NetworkReader.counter = 1

network = createNetwork(collection, tolerance)
print ('Fin construction du réseau 2/5.')



# =============================================================================
#         SUPPRIME LES ARCS EN DOUBLONS
#

# removeDuplicateGeometries(network, seuil_doublon)
print ('Fin suppression des arcs en doublon 3/5.')



# =============================================================================
#         FUSION DES ARCS SIMPLES
#
TE = list(map(int, network.getIndexEdges()))
tkl.NetworkReader.counter = max(TE) + 1

filtreNoeudSimple(network)
print ('Fin fusion des arcs simples 4/5.')




# =============================================================================
#          SUPPRIME LES PETITS ARCS
#



cpt = 0
nb = 1000
while nb > 10 and cpt < 10:
    nb = deleteSmallEdge(network, DIST_MIN_ARC)
    print ('    nb arcs supprimés: ', nb)
    cpt += 1

# plotNetwork(network)


TE = list(map(int, network.getIndexEdges()))
tkl.NetworkReader.counter = max(TE) + 1

filtreNoeudSimple(network)


cpt = 0
nb = 1000
while nb > 10 and cpt < 10:
    nb = deleteSmallEdge(network, DIST_MIN_ARC)
    print ('    nb arcs supprimés: ', nb)
    cpt += 1


filtreNoeudSimple(network)



print ('Fin suppression des petis arcs 5/5.')

plotNetwork(network)


# Sauvegarde dans un fichier
tkl.NetworkWriter.writeToCsv(network, netwokpath)




# =============================================================================


print ("Fin du réseau.")


print ("END SCRIPT 4.")


