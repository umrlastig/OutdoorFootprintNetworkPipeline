# -*- coding: utf-8 -*-

'''
      TOPOLOGIE DU SQUELETTE
'''


import fiona
from shapely.geometry import shape
import progressbar

import tracklib as tkl

from pipeline import createNetwork, filtreNoeudSimple, deleteSmallEdge
from pipeline import removeDuplicateGeometries
from pipeline import skeleton_smoothing



def network(RESPATH, DIST_MIN_ARC, prefix='PT'):

    # Pour la construction du réseau
    tolerance     = 0.1    # 0.05
    seuil_doublon = 0.1


    # =============================================================================
    #          CHARGEMENT DU SQUELETTE

    collection = tkl.TrackCollection()

    squelettepath = RESPATH + 'network/squelette_' + prefix + '.shp'
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
    
    #removeDuplicateGeometries(network, seuil_doublon)
    #print ('Fin suppression des arcs en doublon 3/4.')


    # =============================================================================
    #          SUPPRIME LES parties crochues du squelette
    #


    network.simplify(0, tkl.MODE_SIMPLIFY_REM_POS_DUP, verbose=False)

    #for idx in progressbar.progressbar(network.getEdgesId()):
    #    network.getEdge(idx).geom = skeleton_smoothing(
    #        network.getEdge(idx).geom, 1, 20)

    print ('Fin suppression des parties crochues du squelette 3/4.')



    # =============================================================================
    #         FUSION DES ARCS SIMPLES ET SUPPRIME LES PETITS ARCS
    #
    #TE = list(map(int, network.getIndexEdges()))
    #tkl.NetworkReader.counter = max(TE) + 1


    filtreNoeudSimple(network)


    cpt = 0
    nb = 1000
    while nb > 10 and cpt < 10:
        nb = deleteSmallEdge(network, DIST_MIN_ARC)
        print ('    nb arcs supprimés: ', nb)
        cpt += 1
    filtreNoeudSimple(network)


    cpt = 0
    nb = 1000
    while nb > 10 and cpt < 10:
        nb = deleteSmallEdge(network, DIST_MIN_ARC)
        print ('    nb arcs supprimés: ', nb)
        cpt += 1
    filtreNoeudSimple(network)


    print ('Fin suppression des petis arcs 4/4.')



    network.simplify(0, tkl.MODE_SIMPLIFY_REM_POS_DUP, verbose=False)
    network.simplify(5, tkl.MODE_SIMPLIFY_DOUGLAS_PEUCKER, verbose=False)
    print ('Fin simplification 5/5.')


    # =========================================================================











    # =========================================================================
    # Sauvegarde dans un fichier
    netwokpath = RESPATH + 'network/reseau_' + prefix + '.csv'
    tkl.NetworkWriter.writeToCsv(network, netwokpath)

    print ("Fin de la construction du réseau.")


    
