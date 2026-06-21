# -*- coding: utf-8 -*-


import os
import sys
import csv
csv.field_size_limit(sys.maxsize)

import tracklib as tkl



def load_raw_tracks_split(RESPATH, tracespathsource, fmt, X, Y):
    '''
    Dédié aux traces de Outdoorvision :
        les attributs sont stockés dans le fichier .csv
    '''

    print ('Loading and split outdoorvision track data...')


    """ ======================================================================= """
    """         Reading                                                         """
    """                                                                         """
    print ('Reading track data...')

    poly = tkl.Polygon(X, Y)
    constraintBBox = tkl.Constraint(shape=poly,
                                    mode=tkl.MODE_CROSSES,
                                    type=tkl.TYPE_CUT_AND_SELECT)


    tracks = tkl.TrackSource(tracespathsource, fmt)
    total = len(tracks)
    print ('     Number files to load: ', total)


    """ ======================================================================= """
    """         Découpage                                                       """
    """                                                                         """
    print ('Starting split ...')

    metacollectionpath = resultpath = os.path.join(RESPATH, 'metadata_collection.csv')
    f1 = open(metacollectionpath,'w')
    f1.write("ID;NUM;TRACK_ID;USER_ID;DATE_START\n")

    cpt = 1
    cutCollection = tkl.TrackCollection()

    for track in tracks:
        if cpt%1000 == 0:
            print ('    ', cpt, '/', total)

        ID = 'OV_' + str(cpt)
        cpt += 1

        num = str(int(track.getObsAnalyticalFeature('num', 0)))
        uid = str(int(track.getObsAnalyticalFeature('user_id', 0)))
        tid = str(int(track.getObsAnalyticalFeature('track_id', 0)))
        dstart = str(track.getObsAnalyticalFeature('date_start', 0))

        f1.write(ID + ";" + str(int(num)) + ";" + str(tid) + ";" + str(uid) + ";" + dstart + "\n")

        selection = constraintBBox.select(tkl.TrackCollection([track]))
        if len(selection) <= 0:
            continue

        newtrack = tkl.Track()
        newtrack.tid = ID
        newtrack.uid = ID
        for o in selection.getTrack(0):
            newtrack.addObs(tkl.Obs(tkl.ENUCoords(o.position.getX(), o.position.getY()),
                                    tkl.ObsTime()))
        newtrack.createAnalyticalFeature('TID', str(ID))
        cutCollection.addTrack(newtrack)

    f1.close()


    print ('     Number of tracks after split: ' + str(cutCollection.size()))

    return cutCollection





