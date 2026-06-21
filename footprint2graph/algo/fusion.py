# -*- coding: utf-8 -*-

import time
import tracklib as tkl

from footprint2graph import log_event


"""
Track segments aggregation.

This module provides functions aimed at producing the best geometric 
representation of network edges from a topological skeleton.

It includes a main function that orchestrates the aggregation of track 
segments assigned to skeleton edges with topology, as well as a secondary 
function that performs track segment merging using the tracklib library.


"""


MAX_TRACKS_FOR_FUSION = 100
MODE_FUSION = tkl.MODE_MATCHING_FDTW



def aggregate_track_segments_by_edge(network, SEARCH, RESPATH, iteration_index):
    '''
    Orchestrates track segment aggregation for each edge.

    This function (main) reads all candidate track segments to be merged 
    from files of the form mapmatch/resultmm_<iteration_index>.csv. 

    If an edge length is below the SEARCH threshold, no merging is performed 
    and the original skeleton edge geometry is used instead.

    For each edge, a result file is written containing the edge identifier, 
    median track collection geometry, and number of contributing tracks, 
    stored under geometry/fusion<iteration_index>/<edge_id>.csv.

    The main statistical indicators are saved in aggregate<iteration_index>.json


    Parameters
    ----------
    network : tkl.Network
        The simplified skeleton with a topology.
    SEARCH : float
        Minimum edge length for track merging.
    RESPATH : str
        Output directory for storing results defined in the configuration file.
    iteration_index : int
        Current iteration number.

    Returns
    -------
    merged_tracks : tkl.TrackCollection
        Collection of median tracks per edge. 
    '''
    
    print ("    Starting track segment aggregation for all network edges ...")

    NBAP30 = 0
    NBAM30 = 0
    MIN    = 100000
    MOY    = 0

    pathfusion = 'fusion' + str(iteration_index)
    geompath = RESPATH + 'geometry/' + pathfusion + '/'
    
    # Aggregation with DTW distance
    fusions = tkl.TrackCollection()
    edgeprevious = -1
    TRACES = []
    mmpath = RESPATH + 'mapmatch/resultmm_' + str(iteration_index) + '.csv'
    with open(mmpath, 'r') as file:
        cpt = 0
        for s in file:

            if cpt == 0:
                cpt += 1
                continue

            line = s.split(";")
            if len(line) < 1:
                continue

            #  "EDGE_ID; TID; MID; WKT
            edgeid = line[0]

            if edgeprevious != edgeid and edgeprevious != -1:

                e = network.EDGES[edgeprevious]

                if e.geom.length() <= SEARCH:
                    # print ("        No merge for arc number (length too small):", edgeprevious)
                    central = e.geom.copy()
                    central.createAnalyticalFeature('edgeid', edgeprevious)
                    central.tid = edgeprevious
                    fusions.addTrack(central)

                    # sauvegarde
                    chemin = geompath + str(edgeprevious) + ".csv"
                    f = open(chemin, 'w')
                    f.write("EDGE_ID;TRACKS_SIZE;WKT\n")
                    f.write(str(edgeprevious) + ";" + str(len(TRACES)) + ";" + central.toWKT() + "\n")
                    f.close()

                elif len(TRACES) >= 1:
                    # print ("        Aggregation for arc number:", edgeprevious)
                    central = aggregate_track_segments_on_edge(TRACES)

                    MIN = min([MIN, len(TRACES)])
                    MOY += len(TRACES)
                    if len(TRACES) > MAX_TRACKS_FOR_FUSION:
                        NBAP30 += 1
                    else:
                        NBAM30 += 1
                    if central is not None:
                        central.createAnalyticalFeature('edgeid', edgeprevious)
                        central.tid = edgeprevious
                        fusions.addTrack(central)

                        # sauvegarde
                        chemin = geompath + str(edgeprevious) + ".csv"
                        f = open(chemin, 'w')
                        f.write("EDGE_ID;TRACKS_SIZE;WKT\n")
                        f.write(str(edgeprevious) + ";" + str(len(TRACES)) + ";" + central.toWKT() + "\n")
                        f.close()

                TRACES = []

            tid = line[1]
            mid = line[2]
            wkt = line[3]
            track = tkl.TrackReader.parseWkt(wkt)
            track.tid = mid
            track.uid = tid
            # print (track.uid, track.size(), edgeid)
            if track.size() > 3:
                TRACES.append(track)

            edgeprevious = edgeid


    # dernière trace
    if len(TRACES) >= 1:
        e = network.EDGES[edgeprevious]
        if e.geom.length() <= SEARCH:
            # print ("        No merge for arc number (length too small):", edgeprevious)
            central = e.geom.copy()
            central.createAnalyticalFeature('edgeid', edgeprevious)
            central.tid = edgeprevious
            fusions.addTrack(central)

            # sauvegarde
            chemin = geompath + str(edgeprevious) + ".csv"
            f = open(chemin, 'w')
            f.write("EDGE_ID;TRACKS_SIZE;WKT\n")
            f.write(str(edgeprevious) + ";" + str(len(TRACES)) + ";" + central.toWKT() + "\n")
            f.close()

        else:
            # print ("        Aggregation for arc number:", edgeprevious)
            central = aggregate_track_segments_on_edge(TRACES)
            MIN = min([MIN, len(TRACES)])
            MOY += len(TRACES)
            if len(TRACES) > MAX_TRACKS_FOR_FUSION:
                NBAP30 += 1
            else:
                NBAM30 += 1
            if central is not None:
                central.createAnalyticalFeature('edgeid', edgeprevious)
                central.tid = edgeprevious
                fusions.addTrack(central)
        
                # sauvegarde
                chemin = geompath + str(edgeprevious) + ".csv"
                f = open(chemin, 'w')
                f.write("EDGE_ID;TRACKS_SIZE;WKT\n")
                f.write(str(edgeprevious) + ";" + str(len(TRACES)) + ";" + central.toWKT() + "\n")
                f.close()


    print ('        Number of aggregations:', fusions.size())
    print ("        Number of aggregations with 30 traces:", NBAP30)
    print ("        Number of aggregations with fewer than 30 traces:", NBAM30)
    print ("        Minimum number of traces in aggregation:", MIN)
    if fusions.size() == 0:
        avg = 0
    else:
        avg = round(MOY/fusions.size())
    print ("        Average number of traces in aggregation:", avg)
    print ("        Aggregation process finished.")

    try:
        log_event(RESPATH + "aggregate" + str(iteration_index) + ".json", {
            "Number of aggregations": fusions.size(),
            "Number of aggregations with 30 traces": NBAP30,
            "Number of aggregations with fewer than 30 traces": NBAM30,
            "Minimum number of traces in aggregation": MIN,
            "Average number of traces in aggregation": avg,
            "ts": time.time()
        })
    except Exception as e:
        print (e)
        print ('Error while writing aggregate information to log.')


    return fusions


def aggregate_track_segments_on_edge (TRACKS):
    '''
    Computes the median track representation for a given edge using tracklib.

    The function aggregate_track_segments_on_edge prepares the collection 
    of track segments for merging and calls the **tracklib** algorithm 
    to compute the median track representation for each edge.

    Parameters
    ----------
    TRACKS : tkl.TrackCollection
        Une collection de traces candidates à la fusion

    Returns
    -------
    median_track : tkl.Track
        The merged track, representing the best geometric representation of 
        a set of tracks following exactly the same path, defined from 
        an origin point to a destination.
    '''

    rec = 10
    cv  = 1e-3

    if len(TRACKS) <= 0:
        return None

    candidats = tkl.TrackCollection()
    for track in TRACKS:
        t = tkl.simplify(track, tolerance=0.5,
                         mode=tkl.MODE_SIMPLIFY_DOUGLAS_PEUCKER,
                         verbose=False)
        candidats.addTrack(t)


    NB = candidats.size()
    # print ('        Number of traces to merge (before sampling):', NB)
    if NB > MAX_TRACKS_FOR_FUSION:
        collection = candidats.randNTracks(MAX_TRACKS_FOR_FUSION)
    else:
        collection = candidats


    # print ('        Number of candidates in the aggregation process:', collection.size())
    print ('        Number of candidate tracks / number of sampled tracks',
           NB, "/", collection.size())

    if collection.size() > 1:
        # print ('        Launching Aggregation ...')
        centralDTW = tkl.fusion(collection,
                             master=tkl.MODE_MASTER_MEDIAN_LEN,
                             dim=2,
                             mode=MODE_FUSION,
                             p=2,
                             represent_method=tkl.MODE_REP_BARYCENTRE,
                             agg_method=tkl.MODE_AGG_MEDIAN,
                             constraint=False,
                             verbose=False,
                             iter_max=25,
                             recursive=rec,
                             cv=cv)
        # print ('        Aggregation ended.')
        return centralDTW
    elif candidats.size() == 1:
        print ('    Only one trajectory available for aggregation: no processing required')
        centralDTW = candidats.getTrack(0)
        return centralDTW

    return None


