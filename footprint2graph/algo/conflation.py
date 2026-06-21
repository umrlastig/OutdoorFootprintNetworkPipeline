# -*- coding: utf-8 -*-

import os
import sys
import time

import tracklib as tkl

from tracklib.core import TrackCollection
from tracklib.algo.interpolation import conflate
from tracklib.algo.comparison import compare, MODE_COMPARISON_POINTWISE

from footprint2graph import log_event


# ---------------------------------------------------------------------------------
# Elastic conflation of segment geometries on a network
# ---------------------------------------------------------------------------------
# Inputs: - geom      : a collection of geometries (TrackCollection)
#         - network   : network containing reference nodes
#         - threshold : distance btw ending points above which conflation aborted
#          - h         : covariance distance of elastic correction
# Output: a collection of geometries (TrackCollection) preserving the shape of the 
# input geometries while enforcing constraints on ending points defined by network
# Each object in geom must have a tid matching with edge ids of the network
# ---------------------------------------------------------------------------------
# Conflation is performed with 'colocation least squares' method and gaussian 
# covariogram of standard deviation h
# ---------------------------------------------------------------------------------
def conflateOnNetwork(geom, network, threshold=1e300, h=30,
                      RESPATH=None, prefix=None, verbose=True):
    
    out = TrackCollection()
    if (verbose):
        print("-----------------------------------------------------------------------------------------")
        print("CORRECTION ELASTIQUE DE LA GEOMETRIE DU RESEAU")
        print("-----------------------------------------------------------------------------------------")
    max_total = 0
    rmse_total = 0
    matched = 0
    
    for segment in geom:
        if segment.tid == -1:
            continue
        edge = network.getEdge(segment.tid)
        p1 = edge.source.coord
        p2 = edge.target.coord
        
        h11 = p1.distance2DTo(segment[ 0].position); h12 = p2.distance2DTo(segment[-1].position); h1 = (h11**2+h12**2)**0.5/1.414
        h21 = p1.distance2DTo(segment[-1].position); h22 = p2.distance2DTo(segment[ 0].position); h2 = (h21**2+h22**2)**0.5/1.141
        HMIN = min(h1, h2)
    
        if (h2 < h1):
            ptemp = p1; p1 = p2; p2 = ptemp
        
        
        if (HMIN < threshold):
        
            conflated = conflate(segment, [p1, p2], [0, -1], h)
                
            MED = compare(segment, conflated, mode=MODE_COMPARISON_POINTWISE, p=1)
            MSE = compare(segment, conflated, mode=MODE_COMPARISON_POINTWISE, p=2)
            MAX = compare(segment, conflated, mode=MODE_COMPARISON_POINTWISE, p=float('inf'))
            if (verbose):
                print("#{:6s}      MED: {:6.3f} m      RMSE: {:6.3f} m      MAX: {:6.3f} m      MATCH: {:6.3f} m".format(segment.tid, MED, MSE, MAX, HMIN))
            rmse_total += MSE**2
            max_total = max(max_total, MAX)
            matched += 1
            
        else:
            conflated = segment.copy()
            
        conflated.tid = segment.tid    
        out.addTrack(conflated)
    
    if (len(geom) > 2):
        rmse_total = (rmse_total/len(geom)-1)**0.5
        if (verbose):
            print("-----------------------------------------------------------------------------------------")
            print("Number of conflated segments :     ",   matched, "      ({:2.2f}%)".format(matched/len(geom)*100))
            print("Total distorsion RMSE        :  {:6.3f} m     (MAX: {:6.3f} m)".format(rmse_total, max_total))

        if RESPATH is not None:
            log_event(RESPATH + "conflate" + prefix + ".json", {
                "Number of conflated segments": matched,
                "Percent of conflated segments": matched/len(geom)*100,
                "Total distorsion RMSE (m)": rmse_total,
                "MAX distorsion RMSE (%)": max_total,
                "ts": time.time()
            })


    if (verbose):
        print("-----------------------------------------------------------------------------------------")
    
    return out



def conflateTurnOnTerminalEdge(network, nid, SEARCH, h = 10, log_level='ERROR'):
    '''
    conflate point of maximum curvature with the summit of a terminal edge

    Parameters
    ----------
    network : TYPE
        DESCRIPTION.
    nid : TYPE
        DESCRIPTION.
    SEARCH : TYPE
        DESCRIPTION.
    h : TYPE, optional
        DESCRIPTION. The default is 10.

    Returns
    -------
    None.

    '''

    # print ('    ', nid)
    edges = network.getIncidentEdges(nid)
    #print ('     EDGES : ', len(edges), edges)

    EID0 = edges[0]
    EID1 = edges[1]
    EID2 = edges[2]
    # print (EID0, EID1, EID2)
    if EID1 == EID2:
        # cas des arcs en boucle
        return

    node = network.NODES[nid]

    l1 = network.EDGES[EID0].geom.length()
    l2 = network.EDGES[EID1].geom.length()
    l3 = network.EDGES[EID2].geom.length()

    idx = -1; idx1 = -1; idx2 = -1;

    d = sys.float_info.max
    if l1 < SEARCH:
        nb = len(network.getIncidentEdges(getAutreNoeud(network, EID0, node)[0].id))
        if l1 < d and nb == 1:
            idx = EID0; idx1 = EID1; idx2 = EID2;
            d = l1
    if l2 < SEARCH:
        nb = len(network.getIncidentEdges(getAutreNoeud(network, EID1, node)[0].id))
        if l2 < d and nb == 1:
            idx = EID1;  idx1 = EID0; idx2 = EID2;
            d = l2
    if l3 < SEARCH:
        nb = len(network.getIncidentEdges(getAutreNoeud(network, EID2, node)[0].id))
        if l3 < d and nb == 1:
            idx = EID2;  idx1 = EID0; idx2 = EID1;
            d = l3

    if idx == -1:
        if log_level == 'DEBUG':
            print ('    Conflation cannot be performed for node ', nid,
                   '; the three incident edges are too long:', round(l1),
                   round(l2), round(l3))
        return

    # print (idx, idx1, idx2, node)

    # Au moins 1 arc qui est une feuille
    nb1 = len(network.getIncidentEdges(getAutreNoeud(network, idx, node)[0].id))
    nb2 = len(network.getIncidentEdges(getAutreNoeud(network, idx1, node)[0].id))
    nb3 = len(network.getIncidentEdges(getAutreNoeud(network, idx2, node)[0].id))
    # print (nid, nb1, nb2, nb3)
    if nb1 > 1 and nb2 > 1 and nb3 > 1:
        if log_level == 'DEBUG':
            print ('    Conflation cannot be performed for node ', nid,
                   '; the three incident edges are not leaves')
        return

    # il faut d'abord trouver les trois noeuds
    (n1, pos1) = getAutreNoeud(network, idx, node)
    (n2, pos2) = getNoeud(network, idx1, node)
    (n3, pos3) = getNoeud(network, idx2, node)

    # on crée un nouvel arc en conflatant
    pts = [n1.coord]
    pts_index = [pos2]
    h2 = h
    if h2 > l2:
        h2 = l2*0.9
    s2 = conflate(network.EDGES[idx1].geom, pts, pts_index, h=h2)
    pts_index = [pos3]
    h3 = h
    if h3 > l3:
        h3 = l3*0.9
    s3 = conflate(network.EDGES[idx2].geom, pts, pts_index, h=h3)

    # s3.plot('r-')
    # s2.plot('r-')

    (node1, poss1) = getAutreNoeud(network, idx1, node)
    (node2, poss2) = getAutreNoeud(network, idx2, node)

    # fusionne
    if s2.getLastObs().distance2DTo(s3.getFirstObs()) < 0.001:
        s = s2 + s3
        '''
        # On force le premier point
        op = network.EDGES[idx1].geom.getFirstObs()
        if op.position.distance2DTo(s.getFirstObs().position) > 0.001:
            s.insertObs(op, 0)
        # On force le dernier point
        op = network.EDGES[idx2].geom.getLastObs()
        if op.position.distance2DTo(s.getLastObs().position) > 0.001:
            s.addObs(op)
        '''
    elif s2.getLastObs().distance2DTo(s3.getLastObs()) < 0.001:
        s = s2 + s3.reverse()
        '''
        # On force le premier point
        op = network.EDGES[idx1].geom.getFirstObs()
        if op.position.distance2DTo(s.getFirstObs().position) > 0.001:
            s.insertObs(op, 0)
        # On force le dernier point
        op = network.EDGES[idx2].geom.getFirstObs()
        if op.position.distance2DTo(s.getLastObs().position) > 0.001:
            s.addObs(op)
        '''
    elif s2.getFirstObs().distance2DTo(s3.getLastObs()) < 0.001:
        s = s2.reverse() + s3.reverse()
        '''
        # On force le premier point
        op = network.EDGES[idx1].geom.getLastObs()
        if op.position.distance2DTo(s.getFirstObs().position) > 0.001:
            s.insertObs(op, 0)
        # On force le dernier point
        op = network.EDGES[idx2].geom.getFirstObs()
        if op.position.distance2DTo(s.getLastObs().position) > 0.001:
            s.addObs(op)
        '''
    elif s2.getFirstObs().distance2DTo(s3.getFirstObs()) < 0.001:
        s = s2.reverse() + s3
        '''
        # On force le premier point
        op = network.EDGES[idx1].geom.getLastObs()
        if op.position.distance2DTo(s.getFirstObs().position) > 0.001:
            s.insertObs(op, 0)
        # On force le dernier point
        op = network.EDGES[idx2].geom.getLastObs()
        if op.position.distance2DTo(s.getLastObs().position) > 0.001:
            s.addObs(op)
        '''

    s.setObs(0, tkl.Obs(node1.coord, tkl.ObsTime()))
    s.setObs(s.size()-1, tkl.Obs(node2.coord, tkl.ObsTime()))


    # s.plot('r-')

    edge = tkl.Edge(str(tkl.NetworkReader.counter), s)
    tkl.NetworkReader.counter += 1
    # print (edges[0], edges[1], edges[2])

    n = getAutreNoeud(network, idx1, node)[0]
    noeudIni = tkl.Node(n.id, s.getFirstObs().position.copy())
    n = getAutreNoeud(network, idx2, node)[0]
    noeudFin = tkl.Node(n.id, s.getLastObs().position.copy())

    # On supprime les 3 arcs en commencant par les noeuds
    #     (ce n'est plus nécessaire)
    # network.removeNode(node)
    #if n1.id in network.getNodesId():
    #    network.removeNode(n1)
    #if noeudIni.id in network.getNodesId():
    #    network.removeNode(noeudIni)
    #if noeudFin.id in network.getNodesId():
    #    network.removeNode(noeudFin)

    network.removeEdge(network.EDGES[EID0])
    network.removeEdge(network.EDGES[EID1])
    network.removeEdge(network.EDGES[EID2])
    # print ('    remove edges:', EID0, EID1, EID2)

    network.addEdge(edge, noeudIni, noeudFin)

    # On remet à jour la topologie pour les noeuds noeudIni et noeudFin
    for edge in network:
        ni = edge.source
        nf = edge.target

        if edge.orientation >= 0:
            if edge.id not in network.NEXT_EDGES[ni.id]:
                network.NEXT_EDGES[ni.id].append(edge.id)
            if edge.id not in network.PREV_EDGES[nf.id]:
                network.PREV_EDGES[nf.id].append(edge.id)

            if ni.id not in network.NEXT_NODES:
                network.NEXT_NODES[ni.id] = []
            if nf.id not in network.NEXT_NODES[ni.id]:
                network.NEXT_NODES[ni.id].append(nf.id)
            if nf.id not in network.PREV_NODES:
                network.PREV_NODES[nf.id] = []
            if ni.id not in network.PREV_NODES[nf.id]:
                network.PREV_NODES[nf.id].append(ni.id)

        if edge.orientation <= 0:
            if edge.id not in network.NEXT_EDGES[nf.id]:
                network.NEXT_EDGES[nf.id].append(edge.id)
            if edge.id not in network.PREV_EDGES[ni.id]:
                network.PREV_EDGES[ni.id].append(edge.id)

            if nf.id not in network.NEXT_NODES:
                network.NEXT_NODES[nf.id] = []
            if ni.id not in network.NEXT_NODES[nf.id]:
                network.NEXT_NODES[nf.id].append(ni.id)

            if ni.id not in network.PREV_NODES:
                network.PREV_NODES[ni.id] = []
            if nf.id not in network.PREV_NODES[ni.id]:
                network.PREV_NODES[ni.id].append(nf.id)

        if edge.id not in network.NBGR_EDGES[ni.id]:
            network.NBGR_EDGES[ni.id].append(edge.id)
        if ni.id not in network.NBGR_NODES:
            network.NBGR_NODES[ni.id] = []
        if nf.id not in network.NBGR_NODES[ni.id]:
            network.NBGR_NODES[ni.id].append(nf.id)

        if edge.id not in network.NBGR_EDGES[nf.id]:
            network.NBGR_EDGES[nf.id].append(edge.id)
        if nf.id not in network.NBGR_NODES:
            network.NBGR_NODES[nf.id] = []
        if ni.id not in network.NBGR_NODES[nf.id]:
            network.NBGR_NODES[nf.id].append(ni.id)




def selectNodes(network, node, distance):
    """Selection des autres noeuds dans le cercle dont node.coord est le centre,
    de rayon distance

    :param node: le centre du cercle de recherche.
    :param distance: le rayon du cercle de recherche.

    :return: tableau de NODES liste des noeuds dans le cercle
    """
    NODES = []

    if network.spatial_index is None:
        for key in network.getIndexNodes():
            n = network.NODES[key]
            if n.coord.distance2DTo(node.coord) <= distance:
                NODES.append(n)
    else:
        print ('INDEX !!!!!!')
        vicinity_edges = network.spatial_index.neighborhood(node.coord, unit=1)
        for e in vicinity_edges:
            source = network.EDGES[network.getEdgeId(e)].source
            target = network.EDGES[network.getEdgeId(e)].target
            if source.coord.distance2DTo(node.coord) <= distance:
                NODES.append(source)
            if target.coord.distance2DTo(node.coord) <= distance:
                NODES.append(target)

    return NODES


def getNoeud(network, eid, node):
    edge = network.EDGES[eid]
    nd = edge.source
    na = edge.target

    if node.id == nd.id:
        return (nd, 0)
    if node.id == na.id:
        return (na, edge.geom.size()-1)
    return None


def getAutreNoeud(network, eid, node):
    edge = network.EDGES[eid]
    nd = edge.source
    na = edge.target

    if node.id == nd.id:
        return (na, edge.geom.size()-1)
    if node.id == na.id:
        return (nd, 0)
    return None



