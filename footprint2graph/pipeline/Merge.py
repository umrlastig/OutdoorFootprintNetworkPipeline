# -*- coding: utf-8 -*-

import math
import matplotlib.pyplot as plt
import numpy as np
import os
import tracklib as tkl

from footprint2graph import conflate
from footprint2graph import decoupe_trace, extend_extremity
from footprint2graph import distance_point_track, get_final_edges
from footprint2graph import find_connection_candidate



def mergeNetwork(RESPATH, pipeline_idx = 2, PPV_SEUIL = 20,
                 ELASTIC_COV_DISTANCE = 20, EXTENSION = 50):
    '''
    

    Parameters
    ----------
    respath : TYPE
        DESCRIPTION.
    iteration_index : TYPE
        DESCRIPTION.
    PPV_SEUIL : TYPE
        DESCRIPTION.
    ELASTIC_COV_DISTANCE : TYPE
        DESCRIPTION.
    EXTENSION : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''


    pidx = int (pipeline_idx)

    fusionpath1 = RESPATH + '/geometry/raccord' + str(pidx-1) + '/'
    fusionpath2 = RESPATH + '/geometry/raccord' + str(pidx) + '/'


    # On charge network1
    collection1 = tkl.TrackCollection()
    for fusionfilename in os.listdir(fusionpath1):
        with open(fusionpath1 + fusionfilename, 'r') as file:
            # EDGE_ID;WKT
            line = file.readline()
            line = file.readline()

            wkt = line.split(";")[1].strip()
            track = tkl.TrackReader().parseWkt(wkt)
            compare = False
            dmin = float('inf')
            for t in collection1:
                d = tkl.compare(t, track, tkl.MODE_COMPARISON_NN, p=2, verbose=False)
                if d < dmin:
                    dmin = d
            #print (dmin)
            if line.split(";")[0] == '154' or line.split(";")[0] == '152':
                print (dmin)
            if dmin > 1:
                collection1.addTrack(track)
    
    GEOMS = tkl.Topology.create_geoms_topology(collection1, 1)
    network = tkl.NetworkReader.readNetworkFromListTuple(GEOMS)
    #network.plot('k-', 'ko')
    
    # On charge network2
    collection2 = tkl.TrackCollection()
    for fusionfilename in os.listdir(fusionpath2):
        with open(fusionpath2 + fusionfilename, 'r') as file:
            # EDGE_ID;WKT
            line = file.readline()
            line = file.readline()
            wkt = line.split(";")[1].strip()
            track = tkl.TrackReader().parseWkt(wkt)
            track.createAnalyticalFeature('EDGE_ID', line.split(";")[0])
            collection2.addTrack(track)
    
    print ('Size of collection In  : ', collection1.size())
    print ('Size of collection In+1: ', collection2.size())
    
    
    values = [int(x) for x in network.getIndexEdges()]
    cptEdge = max(values) + 1
    values = [int(x) for x in network.getIndexNodes()]
    cptNode = max(values) + 1


    
    
    # -----------------------------------------------------------------
    #     Apparier les noeuds des extrémités de la trace au réseau,
    #        on conflate dans le cas pour accrocher joliment la trace au réseau
    #
    
    for track in collection2:
    
        # On cherche le vertex de network le plus proche
        trouve1 = False; trouve2 = False;
        idnodeproche1 = -1; idnodeproche2 = -1;
        idx1 = -1; idx2 = -1;
        dcomp1 = 10000000; dcomp2 = 10000000
    
        for idnode in network.getNodesId():
            node = network.NODES[idnode]
            o = node.coord
    
            d1 = o.distanceTo(track.getFirstObs().position)
            d2 = o.distanceTo(track.getLastObs().position)
            if d1 < PPV_SEUIL:
                trouve1 = True
                if d1 < dcomp1:
                    idnodeproche1 = idnode
                    dcomp1 = d1
                    idx1 = 0
            if d2 < PPV_SEUIL:
                trouve2 = True
                if d2 < dcomp2:
                    idnodeproche2 = idnode
                    dcomp2 = d2
                    idx2 = track.size() - 1
    
        if trouve1:
            # on a trouvé un noeud pour le départ de la trace
            node = network.NODES[idnodeproche1]
            o1 = node.coord
            pts = [o1]
            pts_index = [idx1]
    
            # Il faut conflater la trace pour l'attacher au noeud
            h = ELASTIC_COV_DISTANCE
            if h > track.length():
                h = track.length()*0.9
            newtrack = conflate(track, pts, pts_index, h=h)
            noeudIni = node.copy()
        else:
            # On n'a pas trouvé, il faut créer un nouveau noeud
            noeudIni = tkl.Node(str(cptNode), track.getFirstObs().position.copy())
            cptNode += 1
            newtrack = track.copy()
    
        if trouve2:
            # on a trouvé un noeud pour l'arrivée de la trace
            node = network.NODES[idnodeproche2]
            o2 = node.coord
            pts = [o2]
            pts_index = [idx2]
    
            # Il faut conflater la trace pour l'attacher au noeud
            h = ELASTIC_COV_DISTANCE
            if h > track.length():
                h = track.length()*0.9
            newtrack = conflate(newtrack, pts, pts_index, h=h)
            noeudFin = node.copy()
        else:
            # On n'a pas trouvé, il faut créer un nouveau noeud
            noeudFin = tkl.Node(str(cptNode), track.getLastObs().position.copy())
            cptNode += 1
    
    
        edge = tkl.Edge(str(cptEdge), newtrack)
        cptEdge += 1
        network.addEdge(edge, noeudIni, noeudFin)
        #newtrack.plot('r-')
    
    
    netwokpath = RESPATH + 'merge_' + str(pidx) + '/merge_network.csv'
    # print (netwokpath)
    tkl.NetworkWriter.writeToCsv(network, netwokpath)

    print ('Size of collection In+In+1: ', network.size())
    
    # -----------------------------------------------------------------
    #     On détecte les intersections des arcs
    
    index = tkl.SpatialIndex(network)
    
    for edge1 in network:
        idxarcsvoisins = index.neighborhood(edge1.geom, unit=-1)
        for idxvoisin in idxarcsvoisins:
            edge2 = network[idxvoisin]
            if int(edge1.id) <= int(edge2.id):
                continue
    
            if tkl.intersects(edge2.geom, edge1.geom):
                # ce n'est pas une extrémité pour les 2 arcs
    
                pointsI = tkl.intersection(edge1.geom, edge2.geom, withTime=-1)
    
                for intersec in pointsI:
                    extrema1 = intersec.distanceTo(edge1.geom.getFirstObs()) < 0.1 or intersec.distanceTo(edge1.geom.getLastObs()) < 0.1
                    extrema2 = intersec.distanceTo(edge2.geom.getFirstObs()) < 0.1 or intersec.distanceTo(edge2.geom.getLastObs()) < 0.1
                    if extrema1 and extrema2:
                        continue
    
                    # On a une intersection qui est à l'intérieur
                    #    de edge1 et de edge2
                    # print (edge2.id, edge1.id)
    
                    # pour chaque edge on crée 2 traces
                    (s1, s2) = decoupe_trace(edge1.geom, intersec)
                    (s3, s4) = decoupe_trace(edge2.geom, intersec)
    
                    # On transforme les traces en edges dans la topologie
                    e1 = tkl.Edge(str(cptEdge), s1)
                    cptEdge += 1
                    e2 = tkl.Edge(str(cptEdge), s2)
                    cptEdge += 1
                    e3 = tkl.Edge(str(cptEdge), s3)
                    cptEdge += 1
                    e4 = tkl.Edge(str(cptEdge), s4)
                    cptEdge += 1
    
                    n1 = edge1.source
                    n2 = edge1.target
                    n3 = edge2.source
                    n4 = edge2.target
                    nI = tkl.Node(str(cptNode), intersec.position.copy())
                    cptNode += 1
    
                    # On supprime les 2 arcs
                    network.removeEdge(network.EDGES[edge1.id])
                    network.removeEdge(network.EDGES[edge2.id])
                    # print ('    remove edges:', edge1.id, edge2.id)
    
                    # On ajoute les 4 arcs
                    network.addEdge(e1, n1, nI)
                    network.addEdge(e2, nI, n2)
                    network.addEdge(e3, n3, nI)
                    network.addEdge(e4, nI, n4)
    
    
    
    
    netwokpath = RESPATH + 'merge_' + str(pidx) + '/merge_sans_intersection.csv'
    # print (netwokpath)
    tkl.NetworkWriter.writeToCsv(network, netwokpath)
    # print ('')
    print ('Size of collection In+In+1 avec intersection: ', network.size())
    
    
    # -----------------------------------------------------------------
    #     Fusion des arcs d'incidences 2
    
    
    
    
    
    
    # -----------------------------------------------------------------
    #     Raccordement des arcs "seuls" et proches
    
    
    index = tkl.SpatialIndex(network, verbose=False)
    network.spatial_index = index
    
    #print (network.getIndexEdges())
    #print ('')
    
    OP_ARCS_ISOLES = []
    for edge1 in network:
    
        for side, node in [
                ("START", edge1.source),
                ("END", edge1.target)
        ]:
            if len(network.getIncidentEdges(node.id)) != 1:
                continue
    
            # Son extrémité est une extrémité isolée
    
            # On allonge l'arc du côté "final"
            extension = extend_extremity(edge1.geom, EXTENSION, side)
            if extension is None:
                continue
    
            candidate = find_connection_candidate(
                network,
                edge1,
                extension,
                side
            )
    
            if candidate is not None:
                OP_ARCS_ISOLES.append(candidate)
    
    
    
    # On applique le raccordement pour toutes les opérations
    SPLITS = {}
    for candidat in OP_ARCS_ISOLES:
        #print (candidat["edge"], candidat["edge_to_split"], candidat['side'])
        #print (SPLITS)
        #print (candidat["edge_to_split"])
        #print (get_final_edges(candidat["edge_to_split"], SPLITS))
        #print ('')
    
        # Est-ce que le candidat a été splitter ?
        values = get_final_edges(candidat["edge"], SPLITS)
        if len(values) > 1:
            edge1 = None
            side = None
            point_inters = None
            dmin = float('inf')
            for idedge1 in values:
                e1 = network.EDGES[idedge1]
                for sidetmp, node in [
                        ("START", e1.source),
                        ("END", e1.target)
                ]:
                    if len(network.getIncidentEdges(node.id)) != 1:
                        continue
    
                    # Son extrémité est une extrémité isolée
    
                    # On allonge l'arc du côté "final"
                    extension = extend_extremity(e1.geom, EXTENSION, sidetmp)
                    if extension is None:
                        continue
    
                    candidate = find_connection_candidate(
                        network,
                        e1,
                        extension,
                        sidetmp
                    )
    
                    if candidate is not None:
                        if candidate['dist'] < dmin:
                            dmin = candidate['dist']
                            edge1 = e1
                            side = sidetmp
                            point_inters = candidate['intersection']
                            extension = candidate['extension']
                            edge_to_split = candidate["edge_to_split"]
        else:
            edge1 = network.EDGES[candidat["edge"]]
            side = candidat['side']
            point_inters = candidat['intersection']
            extension = candidat['extension']
            edge_to_split = candidat["edge_to_split"]
    
    
        # print ('    edge to split : ', edge_to_split)
        if edge_to_split not in SPLITS:
            idedge = edge_to_split
            edge_a_couper = network.EDGES[idedge]
        else:
            # Faut retrouver le bon edge_a_couper
            idedge = -1
            dinf = float('inf')
    
            for idedge2 in get_final_edges(edge_to_split, SPLITS):
                # print ('    ', idedge2)
                edge2 = network.EDGES[idedge2]
                (d, pos) = distance_point_track(point_inters, edge2.geom)
                '''
# 
  File ~/7_LIB/footprint2graph/footprint2graph/algo/geometry.py:139 in distance_point_track
    d = o.distanceTo(track.getFirstObs())

AttributeError: 'NoneType' object has no attribute 'distanceTo'
                '''
                if d < dinf:
                    idedge = idedge2
                    dinf = d
    
            # print ('nouvel id : ', idedge)
            edge_a_couper = network.EDGES[idedge]
    
    
    
        # -----------------------------------------------------
        # On coupe l'arc
        (s1, s2) = decoupe_trace(edge_a_couper.geom, point_inters)
    
        if s1 is None:
            # On ne découpe pas l'arc
            nI = edge_a_couper.target
        elif s2 is None:
            # On ne découpe pas l'arc
            nI = edge_a_couper.source
        else:
            # On découpe
            # On transforme les traces en edges dans la topologie
            e1 = tkl.Edge(str(cptEdge), s1)
            cptEdge += 1
            e2 = tkl.Edge(str(cptEdge), s2)
            cptEdge += 1
    
            '''
            if candidat["edge_to_split"] not in SPLITS:
                SPLITS[candidat["edge_to_split"]] = []
            SPLITS[candidat["edge_to_split"]].append(e1.id)
            SPLITS[candidat["edge_to_split"]].append(e2.id)
            '''
            if idedge not in SPLITS:
                SPLITS[idedge] = []
            SPLITS[idedge].append(e1.id)
            SPLITS[idedge].append(e2.id)
        
            # On récupère les noeuds
            n1 = edge_a_couper.source
            n2 = edge_a_couper.target
        
            # 1. On crée un noeud pour l'intersection
            nI = tkl.Node(str(cptNode), point_inters.position.copy())
            cptNode += 1
        
            # On supprime l'ancien arc
            network.removeEdge(edge_a_couper)
        
            # On ajoute les 2 arcs
            network.addEdge(e1, n1, nI)
            network.addEdge(e2, nI, n2)
    
    
        # ---------------------------------------------------
    
        # 1. on supprime l'ancienne extrémité de edge1 du réseau
        if side == 'START':
            network.removeNode(edge1.source)
        elif side == 'END':
            network.removeNode(edge1.target)
    
    
        # 2. Adapter le noeud initial de edge 1 qui était isolé !
        if side == 'START':
            connectnode = edge1.target # nf
            edge1.source = nI
        elif side == 'END':
            connectnode = edge1.source # ni
            edge1.target = nI
    
    
        # 3. Topologie pour le nouveau nI et connectnode
        if edge1.orientation >= 0:
            network.NEXT_EDGES[nI.id].append(edge1.id)
            network.NEXT_NODES[nI.id].append(connectnode.id)
            network.PREV_NODES[connectnode.id].append(nI.id)
        if edge1.orientation <= 0:
            network.PREV_EDGES[nI.id].append(edge1.id)
            network.NEXT_NODES[connectnode.id].append(nI.id)
            network.PREV_NODES[nI.id].append(connectnode.id)
        network.NBGR_EDGES[nI.id].append(edge1.id)
        network.NBGR_NODES[nI.id].append(connectnode.id)
        network.NBGR_NODES[connectnode.id].append(nI.id)
    
    
        # 4. On modifie la géométrie de edge1
        if side == 'START':
            edge1.geom.insertObs(tkl.Obs(point_inters.position, tkl.ObsTime()), 0)
        elif side == 'END':
            edge1.geom.addObs(tkl.Obs(point_inters.position, tkl.ObsTime()))
    
    
        # 5. on modifie l'index car nouvelle géométrie de edge1
        if not network.spatial_index is None:
            idx = network.getIndexEdges().index(edge1.id)
            network.spatial_index.removeFeature(idx)
            network.spatial_index.addFeature(edge1.geom, idx)
    
        index = tkl.SpatialIndex(network, verbose=False)
        network.spatial_index = index

        # ---------------------------------------------------
        #print (SPLITS)
        #if edge1.id == '23':
        #    break
    
    
    
    netwokpath = RESPATH + 'merge_' + str(pidx) + '/merge_extension.csv'
    #print (netwokpath)
    tkl.NetworkWriter.writeToCsv(network, netwokpath)
    print ('Size of collection In+In+1 avec intersection et raccordement: ', network.size())
    
    # -----------------------------------------------------------------------------
    #     Fusion des arcs similaires
    
    
    
    # -----------------------------------------------------------------------------
    #     Fusion des noeuds proches (on en a ajouté, ça vaut le coup)
    
    
    
    
    
    # -----------------------------------------------------------------
    #
    # network.plot('b-', 'bo')
    #plt.xlim([947989, 951188])
    #plt.ylim([6510698, 6513094])
    #plt.show()


    # -----------------------------------------------------------------------------
    #     Reconstruction de la topologie


    GEOMS = tkl.Topology.create_geoms_topology(network.getAllEdgeGeoms(), 0.5)
    network = tkl.NetworkReader.readNetworkFromListTuple(GEOMS)
    print ('Size of reseau de mobilité: ', network.size())

    name = 'reseau_mobilite_' + str(pidx) + '.csv'
    netwokpath = RESPATH + 'merge_' + str(pidx) + '/' + name
    tkl.NetworkWriter.writeToCsv(network, netwokpath)



