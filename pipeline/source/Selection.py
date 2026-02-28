# -*- coding: utf-8 -*-


import tracklib as tkl



def decoup_resample(RESPATH, tracespathsource, NB_OBS_MIN, DIST_MAX_2OBS, X, Y):

    print ("Starting segmentation and resampling...")

    RESAMPLE_SIZE_GRID = 1
    RESAMPLE_SIZE_FUSION = 5


    """ ======================================================================= """
    """         Reading                                                         """
    """                                                                         """

    fmt = tkl.TrackFormat({'ext': 'CSV',
                           'srid': 'ENU',
                           'id_E': 1, 'id_N': 0, 'id_U': 3, 'id_T': 2,
                           'time_fmt': '2D/2M/4Y 2h:2m:2s',
                           'separator': ';',
                           'header': 0,
                           'cmt': '#',
                           'read_all': True})
    rawCollection = tkl.TrackReader.readFromFile(tracespathsource, fmt)
    print ('Finished reading track data.')



    """ ======================================================================= """
    """         Segmentation                                                    """
    """                                                                         """

    print ('Starting segmentation ...')

    poly = tkl.Polygon(X, Y)
    constraintBBox = tkl.Constraint(shape=poly,
                                    mode=tkl.MODE_CROSSES,
                                    type=tkl.TYPE_CUT_AND_SELECT)

    # We prepare the new tracks collection
    cpt = 1
    cutCollection = tkl.TrackCollection()
    for trace in rawCollection:
        num = str(trace.getObsAnalyticalFeature('num', 0))
        uid = str(trace.getObsAnalyticalFeature('user_id', 0))
        tid = str(trace.getObsAnalyticalFeature('track_id', 0))

        if cpt%200 == 0:
            print ('    ', cpt, '/', rawCollection.size())
        cpt += 1

        selection = constraintBBox.select(tkl.TrackCollection([trace]))
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

    print ('    Number of tracks after segmentation: ' + str(cutCollection.size()))


    """ ======================================================================= """
    """         Saving                                                          """
    """                                                                         """
    af_names = ['num', 'track_id', 'user_id', 'version']
    tracespath = RESPATH + "decoup/"
    tkl.TrackWriter.writeToFiles(cutCollection, tracespath,
                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                 h=1, separator=";", af_names=af_names)
    
    print ("Finished saving segmented tracks.")




    # =============================================================================
    #         Resampling spatial
    #

    print ('Starting resampling ...')

    collectionGrid = tkl.TrackCollection()
    collectionFusion = tkl.TrackCollection()
    for trace in cutCollection:
        num = str(trace.getObsAnalyticalFeature('num', 0))
        track_id = str(trace.getObsAnalyticalFeature('track_id', 0))
        user_id = str(trace.getObsAnalyticalFeature('user_id', 0))
        version = str(trace.getObsAnalyticalFeature('version', 0))

        if cpt%100 == 0:
            print ('   ', cpt, '/', cutCollection.size())


        trackG = trace.copy()
        trackG.resample(RESAMPLE_SIZE_GRID, mode=tkl.MODE_SPATIAL)
        trackG.uid = user_id
        trackG.tid = track_id
        trackG.createAnalyticalFeature('num', num)
        trackG.createAnalyticalFeature('track_id', track_id)
        trackG.createAnalyticalFeature('user_id', user_id)
        trackG.createAnalyticalFeature('version', version)
        collectionGrid.addTrack(trackG)

        trackF = trace.copy()
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




    # =============================================================================
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



    # =============================================================================
    print ("Stage 1 finished: segmentation and resampling.")






