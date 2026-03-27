# -*- coding: utf-8 -*-

import math
import os
import sys
import csv
csv.field_size_limit(sys.maxsize)

import tracklib as tkl



def decoup_resample(RESPATH, tracespathsource, X, Y,
                    NB_OBS_MIN = 10, DIST_MAX_2OBS = 50,
                    resampleSizeGrid = 1, resampleSizeFusion = 5):

    print ("Starting segmentation and resampling...")

    RESAMPLE_SIZE_GRID   = resampleSizeGrid
    RESAMPLE_SIZE_FUSION = resampleSizeFusion


    """ ======================================================================= """
    """         Reading                                                         """
    """                                                                         """

    print ('Reading track data...')
    fmt = tkl.TrackFormat({'ext': 'CSV',
                           'srid': 'ENU',
                           'id_E': 1, 'id_N': 0, 'id_U': 3, 'id_T': 2,
                           'time_fmt': '2D/2M/4Y 2h:2m:2s',
                           'separator': ';',
                           'header': 0,
                           'cmt': '#',
                           'read_all': True})

    poly = tkl.Polygon(X, Y)
    constraintBBox = tkl.Constraint(shape=poly,
                                    mode=tkl.MODE_CROSSES,
                                    type=tkl.TYPE_CUT_AND_SELECT)


    tracks = tkl.TrackSource(tracespathsource, fmt)
    total = len(tracks)
    print ('Number files to load: ', total)


    """ ======================================================================= """
    """         Segmentation                                                    """
    """                                                                         """
    print ('Starting segmentation ...')

    cpt = 1
    cutCollection = tkl.TrackCollection()

    for track in tracks:

        if cpt%500 == 0:
            print ('    ', cpt, '/', total)
        cpt += 1

        num = str(track.getObsAnalyticalFeature('num', 0))
        uid = str(track.getObsAnalyticalFeature('user_id', 0))
        tid = str(track.getObsAnalyticalFeature('track_id', 0))

        selection = constraintBBox.select(tkl.TrackCollection([track]))
        if len(selection) <= 0:
            continue

        idxSelect = 1
        o1 = None
        newtrack = tkl.Track()
        newtrack.uid = uid
        newtrack.tid = tid
        for o2 in selection.getTrack(0):
            if o1 is not None:
                if o1.distance2DTo(o2) > DIST_MAX_2OBS:
                    # on coupe la trace pour créer un nouveau morceau
                    if newtrack.size() >= NB_OBS_MIN:
                        newtrack.createAnalyticalFeature('num', num)
                        newtrack.createAnalyticalFeature('user_id', uid)
                        newtrack.createAnalyticalFeature('track_id', tid)
                        version = "v" + str(idxSelect)
                        newtrack.createAnalyticalFeature('version', version)
                        cutCollection.addTrack(newtrack)
                        idxSelect += 1
                    newtrack = tkl.Track()
                    newtrack.uid = uid
                    newtrack.tid = tid
            newtrack.addObs(tkl.Obs(tkl.ENUCoords(o2.position.getX(), o2.position.getY()), o2.timestamp.copy()))
            o1 = o2
    
        # Last track segment
        if newtrack.size() >= NB_OBS_MIN:
            newtrack.createAnalyticalFeature('num', num)
            newtrack.createAnalyticalFeature('user_id', uid)
            newtrack.createAnalyticalFeature('track_id', tid)
            version = "v" + str(idxSelect)
            newtrack.createAnalyticalFeature('version', version)
            cutCollection.addTrack(newtrack)

    print ('     Number of tracks after segmentation: ' + str(cutCollection.size()))


    """ ======================================================================= """
    """         Saving                                                          """
    """                                                                         """

    af_names = ['num', 'track_id', 'user_id', 'version']
    tracespath = RESPATH + "decoup/"

    tkl.TrackWriter.writeToFiles(cutCollection, tracespath,
                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                 h=1, separator=";", af_names=af_names)

    print ("Finished saving segmented tracks.")


    # =========================================================================
    #

    



    # =========================================================================
    #         Resampling spatial
    #

    print ('Starting resampling ...')

    collectionGrid = tkl.TrackCollection()
    collectionFusion = tkl.TrackCollection()

    tracks = tkl.TrackSource(tracespath, fmt)
    total = len(tracks)
    print ('Number files to load: ', total)


    for track in tracks:
        num = str(track.getObsAnalyticalFeature('num', 0))
        track_id = str(track.getObsAnalyticalFeature('track_id', 0))
        user_id = str(track.getObsAnalyticalFeature('user_id', 0))
        version = str(track.getObsAnalyticalFeature('version', 0))

        if cpt%100 == 0:
            print ('   ', cpt, '/', total)


        trackG = track.copy()
        trackG.resample(RESAMPLE_SIZE_GRID, mode=tkl.MODE_SPATIAL)
        trackG.uid = user_id
        trackG.tid = track_id
        trackG.createAnalyticalFeature('num', num)
        trackG.createAnalyticalFeature('track_id', track_id)
        trackG.createAnalyticalFeature('user_id', user_id)
        trackG.createAnalyticalFeature('version', version)
        collectionGrid.addTrack(trackG)

        trackF = track.copy()
        trackF.resample(RESAMPLE_SIZE_FUSION, mode=tkl.MODE_SPATIAL)
        trackF.uid = user_id
        trackF.tid = track_id
        trackF.createAnalyticalFeature('num', num)
        trackF.createAnalyticalFeature('track_id', track_id)
        trackF.createAnalyticalFeature('user_id', user_id)
        trackF.createAnalyticalFeature('version', version)
        collectionFusion.addTrack(trackF)


    print ('    Number of tracks after resampling:', str(collectionGrid.size()))
    print ('    Number of tracks after resampling:', str(collectionFusion.size()))




    # =========================================================================
    #        Enregistrement
    #

    af_names = ['num', 'track_id', 'user_id', 'version']
    
    resampledtracespath = RESPATH + 'resample_grid/'
    tkl.TrackWriter.writeToFiles(collectionGrid, resampledtracespath,
                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                 h=1, separator=";", af_names=af_names)

    resampledtracespath = RESPATH + 'resample_fusion/'
    tkl.TrackWriter.writeToFiles(collectionFusion, resampledtracespath,
                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                 h=1, separator=";", af_names=af_names)

    print ("Finished saving resampled tracks.")




    # =========================================================================
    print ("Stage 1 finished: segmentation and resampling.")







def second_round(RESPATH, NB_OBS_MIN = 10, DIST_MAX_2OBS = 50, RESAMPLE_SIZE_GRID = 1,
                 rep='points_not_mm_1', pathtmm='tmm'):

    buffer_size = 5
    k = 0.6

    OPT_PLUS_PTS = True
    NB_PTS = 4


    # =========================================================================
    #   Lecture des traces découpées et ré-échantillonnées.
    #

    collection = tkl.TrackCollection()
    mmtrackpath = RESPATH + '/mapmatch/' + pathtmm + '/'
    for mmfilename in os.listdir(mmtrackpath):
        #N;E;time;U;num;track_id;user_id;hmm_inference;mmtype;idedge
        fmt = tkl.TrackFormat({'ext': 'CSV',
                               'srid': 'ENU',
                               'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                               'separator': ';',
                               'header': 0,
                               'comment': '#',
                               'read_all': True})
        trace = tkl.TrackReader.readFromFile(mmtrackpath + mmfilename, fmt)
        collection.addTrack(trace)
    print ('Number of tracks map matched :', collection.size())

    # index =  tkl.SpatialIndex(collection)

    cpt = 1
    morceaux = tkl.TrackCollection()


    for i in range(collection.size()):
        track = collection.getTrack(i)
        pkid = track.tid
        # print (pkid)

        num = track.getObsAnalyticalFeature('num', 0)
        track_id = track.getObsAnalyticalFeature('track_id', 0)
        user_id = track.getObsAnalyticalFeature('user_id', 0)
        #version = track.getObsAnalyticalFeature('version', 0)

        cptNot = 0
        morceau = tkl.Track()
        morceau.tid = cpt
        morceau.uid = cpt

        cpt += 1
        for j in range(track.size()):
            obs = track.getObs(j)

            if str(track["mmtype", j]) == "NOT":
                cptNot += 1

                # On modifie un petit peu la position
                # POINTS = index.neighborhood(obs.position, None, buffer_size)
                # TODO : il faudrait trouver le barycentre et faire le kième de la distance encore
                # print (len(POINTS))

                morceau.addObs(obs.copy())

            else:
                if cptNot >= NB_OBS_MIN:
                    if OPT_PLUS_PTS:
                        # on ajoute 4 points avant
                        o1 = track[j]
                        for k in range(j-1, j-NB_PTS-1, -1):
                            o2 = track[k]
                            if o1.distance2DTo(o2) <= DIST_MAX_2OBS:
                                morceau.insertObs(o2, k)
                            o1 = o2
                        # on ajoute 4 points après
                        o1 = track[j]
                        for k in range(j+1, min(j+NB_PTS+1, track.size())):
                            o2 = track[k]
                            if o1.distance2DTo(o2) <= DIST_MAX_2OBS:
                                morceau.addObs(o2)
                            o1 = o2

                    morceau.resample(RESAMPLE_SIZE_GRID, mode=tkl.MODE_SPATIAL)
                    morceau.createAnalyticalFeature('num', num)
                    morceau.createAnalyticalFeature('user_id', user_id)
                    morceau.createAnalyticalFeature('track_id', track_id)
                    morceau.createAnalyticalFeature('version', 'v1')
                    morceaux.addTrack(morceau)

                morceau = tkl.Track()
                morceau.tid = cpt
                morceau.uid = cpt

                cpt += 1
                cptNot = 0

        if cptNot >= NB_OBS_MIN:
            if OPT_PLUS_PTS:
                # on ajoute 4 points avant
                o1 = track[j]
                for k in range(j-1, j-NB_PTS, -1):
                    o2 = track[k]
                    if o1.distance2DTo(o2) <= DIST_MAX_2OBS:
                        morceau.insertObs(o2, k)
                    o1 = o2
                # on ajoute 4 points après
                o1 = track[j]
                for k in range(j+1, min(j+NB_PTS+1, track.size())):
                    o2 = track[k]
                    if o1.distance2DTo(o2) <= DIST_MAX_2OBS:
                        morceau.addObs(o2)
                    o1 = o2
            morceau.resample(RESAMPLE_SIZE_GRID, mode=tkl.MODE_SPATIAL)
            morceau.createAnalyticalFeature('num', num)
            morceau.createAnalyticalFeature('user_id', user_id)
            morceau.createAnalyticalFeature('track_id', track_id)
            morceau.createAnalyticalFeature('version', 'v1')
            morceaux.addTrack(morceau)


    # On enregistre
    # print (morceaux.size())

    af_names = ['num', 'track_id', 'user_id', 'version']

    tracespath = RESPATH + rep + "/"
    tkl.TrackWriter.writeToFiles(morceaux, tracespath,
                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                 h=1, separator=";", af_names=af_names)

