# -*- coding: utf-8 -*-

'''
        TOPOLOGIE DU SQUELETTE
'''


import tracklib as tkl
from geonetlib.toolkit import createNetwork, filtreNoeudSimple, deleteSmallEdge
from geonetlib.toolkit import removeDuplicateGeometries

from tracklib.util.qgis import QGIS, LineStyle, PointStyle
from . import plotNetwork


try:
    from qgis.PyQt.QtCore import QVariant
    from qgis.core import QgsStyle, QgsColorRampShader, QgsColorRampShader, QgsRasterShader
    from qgis.core import QgsSingleBandPseudoColorRenderer, QgsRasterLayer, QgsProject
    from qgis.core import QgsCoordinateReferenceSystem, QgsVectorLayer, QgsFeatureRequest
    from qgis.core import QgsField, QgsGeometry, QgsFeature, QgsVectorFileWriter
    from PyQt5.QtGui import QColor
    import processing
    from qgis.core import edit
except ImportError:
    print ('Code running in a no qgis environment')




def network(RESPATH, tolerance, seuil_doublon, DIST_MIN_ARC):

    # =============================================================================
    #          CHARGEMENT DU SQUELETTE

    squelettepath = RESPATH + 'image/squelette.shp'
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
    netwokpath = RESPATH + 'network/reseau.csv'
    tkl.NetworkWriter.writeToCsv(network, netwokpath)
    
    
    
    
    # =============================================================================

    print ("Fin du réseau.")
    print ("END SCRIPT 4.")


