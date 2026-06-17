# -*- coding: utf-8 -*-

import math
import tracklib as tkl


"""

- snap_lines_to_connect

- line_distance
- nearest_points

- segment_distance


"""


def snap_lines_to_connect(collection, tolerance=1):
    """
    Accroche 2 traces d'une même collection.
    """

    # On indexe la collection pour rechercher uniquement les traces candidates
    #    qui par définition sont proches.
    index = tkl.SpatialIndex(collection)

    # Compteur pour les nouvelles traces
    cptTrack = collection.size() + 1

    for track1 in collection:

        for track2 in collection:
            if track1.tid == track2.tid:
                continue

            if not tkl.intersects(track1, track2):

                # Vérifier la distance
                dist = line_distance(track1, track2)
                if dist < tolerance and dist > 0.0:
                    # print("    Snap needed", track1.tid, track2.tid)


                    # Trouver les points les plus proches pour les 2 traces
                    idxi, idxj = nearest_points(track1, track2)
                    p2 = track2.getObs(idxj).position


                    # On remplace dans la première trace le point
                    #             le plus proche pour qu'il soit dans trace 2
                    track1.setObs(idxi, tkl.Obs(p2, tkl.ObsTime()))


                    # On coupe la trace 1 si besoin
                    if idxi > 0 and idxi < track1.size()-1:
                        print ('    on coupe la trace 1')
                        # on crée 2 nouvelles traces
                        s1 = track1.extract(0, idxi)
                        s1.tid = cptTrack
                        cptTrack += 1
                        collection.addTrack(s1)

                        s2 = track1.extract(idxi, track1.size()-1)
                        s2.tid = cptTrack
                        cptTrack += 1
                        collection.addTrack(s2)

                        # on supprime la track1
                        collection.removeTrack(track1)


                    # On coupe la trace qui doit l'être
                    if idxj > 0 and idxj < track2.size()-1:
                        print ('    on coupe la trace 2')
                        # on en crée 2 nouveaux
                        s1 = track2.extract(0, idxj)
                        s1.tid = cptTrack
                        cptTrack += 1
                        collection.addTrack(s1)

                        s2 = track2.extract(idxj, track2.size()-1)
                        s2.tid = cptTrack
                        cptTrack += 1
                        collection.addTrack(s2)

                        # on supprime la track2
                        collection.removeTrack(track2)


    return collection




def segment_distance(a1, a2, b1, b2):
    return min (
        tkl.distance_to_segment(a1.getX(), a1.getY(), b1.getX(), b1.getY(), b2.getX(), b2.getY()),
        tkl.distance_to_segment(a2.getX(), a2.getY(), b1.getX(), b1.getY(), b2.getX(), b2.getY()),
        tkl.distance_to_segment(b1.getX(), b1.getY(), a1.getX(), a1.getY(), a2.getX(), a2.getY()),
        tkl.distance_to_segment(b2.getX(), b2.getY(), a1.getX(), a1.getY(), a2.getX(), a2.getY()),
    )


def line_distance(track1, track2):
    min_dist = float('inf')

    for i in range(track1.size() - 1):
        p1i = track1.getObs(i).position
        p1i1 = track1.getObs(i+1).position
        for j in range(track2.size() - 1):
            p2j = track2.getObs(j).position
            p2j1 = track2.getObs(j+1).position
            d = segment_distance (p1i, p1i1, p2j, p2j1)
            min_dist = min(min_dist, d)

    return min_dist


def nearest_points(track1, track2):
    maxd = float('inf')
    idxi = -1
    idxj = -1
    for i in range(track1.size()):
        o1 = track1.getObs(i)
        for j in range(track2.size()):
            o2 = track2.getObs(j)
            d = o1.position.distance2DTo(o2.position)
            if d < maxd:
                idxi = i
                idxj = j
                maxd = d
    return (idxi, idxj)


def distance_point_track(o, track):
    pos = 0
    d = o.distanceTo(track.getFirstObs())

    for i in range(1, track.size()):
        if o.distanceTo(track.getObs(i)) < d:
            pos = i
            d = o.distanceTo(track.getObs(i))
    return (d, pos)


def decoupe_trace(track, I):
    '''
    Pas de topologie, uniquement la géométrie qu'on découpe
    '''

    # Trouver le point de la trace le plus proche
    dmin1 = float('inf')
    i1 = -1
    for i in range(len(track)):
        oi = track.getObs(i)
        d = oi.position.distance2DTo(I.position)
        if d < dmin1:
            dmin1 = d
            i1 = i

    # On remplace dans la trace le point d'intersection
    track.setObs(i1, tkl.Obs(I.position.copy(), tkl.ObsTime()))

    s1 = None
    s2 = None

    # On coupe la trace à ce nouveau point d'intersection
    if i1 > 0 and i1 < track.size()-1:
        # on crée 2 nouvelles traces
        s1 = track.extract(0, i1)
        s2 = track.extract(i1, track.size()-1)
    elif i1 == 0:
        s1 = None
        s2 = track
    elif i1 == track.size()-1:
        s1 = track
        s2 = None

    return (s1, s2)



def extend_extremity(track, length=50, pos='END', verbose=True):
    '''
    Extend start point or end point 

    Parameters
    ----------
    track : TYPE
        DESCRIPTION.
    length : TYPE, optional
        DESCRIPTION. The default is 50.
    pos : {'START', 'END'}, optional
        DESCRIPTION. The default is 'END'.

    Returns
    -------
    track : TYPE
        DESCRIPTION.

    '''

    track.removePosDup()
    if track.size() < 2:
        if verbose:
            print ("        Track contains too few points (" + str(track.size()) + ")")
        return None

    if pos == 'END':
        p1 = track[-2]
        p2 = track[-1]
    else:
        p1 = track[1]
        p2 = track[0]

    if p1.position == p2.position:
        if verbose:
            print ("        Track contains same points.")
        return None

    dx = p2.position.getX() - p1.position.getX()
    dy = p2.position.getY() - p1.position.getY()

    norm = math.hypot(dx, dy)

    dx /= norm
    dy /= norm

    p3 = (
        p2.position.getX() + length * dx,
        p2.position.getY() + length * dy
    )

    track = tkl.Track()
    c2 = tkl.ENUCoords(p2.position.getX(), p2.position.getY())
    track.addObs(tkl.Obs(c2, tkl.ObsTime()))
    c3 = tkl.ENUCoords(p3[0], p3[1])
    track.addObs(tkl.Obs(c3, tkl.ObsTime()))

    return track


def get_final_edges(edge_id, splits):
    '''
    Récupére les arcs terminaux de edge_id dans l'arbre de découpage SPLITS

    Parameters
    ----------
    edge_id : TYPE
        DESCRIPTION.
    splits : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    '''

    if edge_id not in splits:
        return [edge_id]

    result = []

    for child in splits[edge_id]:
        result.extend(get_final_edges(child, splits))

    return result



def find_connection_candidate(network, edge, extension, side):
    """
    Search for the closest intersection between an extension and a neighboring edge.
    """

    if side == "START":
        ref_pos = edge.geom.getFirstObs().position
    else:
        ref_pos = edge.geom.getLastObs().position

    point_inters = None
    edge_to_split = None
    min_dist = float("inf")

    neighbor_idxs1 = network.spatial_index.neighborhood(edge.geom, unit=-1)
    neighbor_idxs2 = network.spatial_index.neighborhood(extension, unit=-1)
    neighbor_idxs = set(neighbor_idxs1) | set(neighbor_idxs2)

    for idx in neighbor_idxs:
        neighbor = network[idx]
        if neighbor.id == edge.id:
            continue

        intersections = tkl.intersection(extension, neighbor.geom, withTime=-1)
        for intersec in intersections:

            dist = intersec.position.distance2DTo(ref_pos)

            if dist < min_dist:
                min_dist = dist
                point_inters = intersec
                edge_to_split = neighbor

    if edge_to_split is None:
        return None

    return {
        "edge": edge.id,
        "side": side,
        "intersection": point_inters,
        "edge_to_split": edge_to_split.id,
        "extension": extension,
        "dist": min_dist
    }




