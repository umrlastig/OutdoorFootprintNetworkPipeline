# -*- coding: utf-8 -*-

'''
      TOPOLOGIE DU SQUELETTE
'''


import fiona
from shapely.geometry import shape
import progressbar

import tracklib as tkl
from util import createNetwork, filtreNoeudSimple, deleteSmallEdge
from util import removeDuplicateGeometries
from util import skeleton_smoothing





def network(RESPATH, tolerance, seuil_doublon, DIST_MIN_ARC):

    # =============================================================================
    #          CHARGEMENT DU SQUELETTE

    collection = tkl.TrackCollection()

    squelettepath = RESPATH + 'network/squelette.shp'
    with fiona.open(squelettepath, 'r') as shapefile:
        for feature in shapefile:
            # 1 MultiLineString
            geom = shape(feature['geometry'])
            if geom.geom_type == "MultiLineString":
                for line in geom.geoms:
                    track = tkl.TrackReader().parseWkt(line.wkt)
                    if track.length() < tolerance/2:
                        continue
                    collection.addTrack(track)

    print ('Nb lignes : ', collection.size())
    print ('Fin chargement des données 1/4.')



    # =============================================================================
    #             CONSTRUCTION RESEAU
    #
    tkl.NetworkReader.counter = 1
    
    network = createNetwork(collection, tolerance)
    print ('Fin construction du réseau 2/4.')



    # =============================================================================
    #         SUPPRIME LES ARCS EN DOUBLONS
    #
    
    removeDuplicateGeometries(network, seuil_doublon)
    print ('Fin suppression des arcs en doublon 3/4.')


    # =============================================================================
    #          SUPPRIME LES parties crochues du squelette
    #


    network.simplify(0, tkl.MODE_SIMPLIFY_REM_POS_DUP, verbose=False)
    for idx in progressbar.progressbar(network.getEdgesId()):
        network.getEdge(idx).geom = skeleton_smoothing(
            network.getEdge(idx).geom, 1, 20)

    print ('Fin suppression des parties crochues du squelette 3/4.')



    # =============================================================================
    #         FUSION DES ARCS SIMPLES ET SUPPRIME LES PETITS ARCS
    #
    #TE = list(map(int, network.getIndexEdges()))
    #tkl.NetworkReader.counter = max(TE) + 1
    
    # filtreNoeudSimple(network)


    cpt = 0
    nb = 1000
    while nb > 10 and cpt < 10:
        nb = deleteSmallEdge(network, DIST_MIN_ARC)
        print ('    nb arcs supprimés: ', nb)
        cpt += 1
    # filtreNoeudSimple(network)


    print ('Fin suppression des petis arcs 4/4.')



    # =============================================================================
    # Sauvegarde dans un fichier
    netwokpath = RESPATH + 'network/reseau.csv'
    tkl.NetworkWriter.writeToCsv(network, netwokpath)

    print ("Fin de la construction du réseau.")



