# -*- coding: utf-8 -*-

import tracklib as tkl



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

    # On coupe la trace à ce nouveau point d'intersection
    if i1 > 0 and i1 < track.size()-1:
        print ('        Splitting track')
        # on crée 2 nouvelles traces
        s1 = track.extract(0, i1)
        s2 = track.extract(i1, track.size()-1)

    return (s1, s2)

