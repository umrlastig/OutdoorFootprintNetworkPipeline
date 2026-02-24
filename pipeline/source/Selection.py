# -*- coding: utf-8 -*-


import tracklib as tkl



def decoup_resample(RESPATH, tracespathsource, NB_OBS_MIN, DIST_MAX_2OBS, X, Y,
                    RESAMPLE_SIZE_GRID, RESAMPLE_SIZE_FUSION):

    print ("Lancement du découpage et ré-échantillonnage ...")


    """ ======================================================================= """
    """         Lecture                                                         """
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
    print ('Fin de la lecture des traces.')



    """ ======================================================================= """
    """         Découpage                                                       """
    """                                                                         """
    
    poly = tkl.Polygon(X, Y)
    constraintBBox = tkl.Constraint(shape=poly,
                                    mode=tkl.MODE_CROSSES,
                                    type=tkl.TYPE_CUT_AND_SELECT)

    # On prépare la nouvelle collection de traces
    cpt = 1
    cutCollection = tkl.TrackCollection()
    for trace in rawCollection:
    
        if cpt%200 == 0:
            print ('   ', cpt, '/', rawCollection.size())
        cpt += 1

        selection = constraintBBox.select(tkl.TrackCollection([trace]))
        if len(selection) <= 0:
            continue

        idxSelect = 1
        o1 = None
        tn = tkl.Track()
        for o2 in selection.getTrack(0):
            if o1 is not None:
                if o1.distance2DTo(o2) > DIST_MAX_2OBS:
                    # on coupe la trace pour créer un nouveau morceau
                    if tn.size() >= NB_OBS_MIN:
                        tn.uid = str(trace.getObsAnalyticalFeature('user_id', 0)) + "-"+ str(idxSelect)
                        tn.tid = str(trace.getObsAnalyticalFeature('track_id', 0)) + "-"+ str(idxSelect)
                        tn.createAnalyticalFeature('num', trace.getObsAnalyticalFeature('num', 0))
                        tn.createAnalyticalFeature('user_id', tn.uid)
                        tn.createAnalyticalFeature('track_id', tn.tid)
                        cutCollection.addTrack(tn)
                        idxSelect += 1
                    tn = tkl.Track()
            tn.addObs(o2)
            o1 = o2
    
        # Dernier morceau de trace
        if tn.size() >= NB_OBS_MIN:
            tn.uid = str(trace.getObsAnalyticalFeature('user_id', 0)) + "-"+ str(idxSelect)
            tn.tid = str(trace.getObsAnalyticalFeature('track_id', 0)) + "-"+ str(idxSelect)
            tn.createAnalyticalFeature('num', trace.getObsAnalyticalFeature('num', 0))
            tn.createAnalyticalFeature('user_id', tn.uid)
            tn.createAnalyticalFeature('track_id', tn.tid)
            cutCollection.addTrack(tn)
    
    
    print ('    Nombre de traces après découpage : ' + str(cutCollection.size()))


    
    """ ======================================================================= """
    """         Enregistrement des données                                      """
    """                                                                         """
    af_names = ['num', 'track_id', 'user_id']
    tracespath = RESPATH + "decoup/"
    tkl.TrackWriter.writeToFiles(cutCollection, tracespath,
                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                 h=1, separator=";", af_names=af_names)
    
    print ("Fin de l'enregistrement des traces découpées.")




    # =============================================================================
    #         Resampling spatial
    #

    print ('    Début ré-échantillonnage')

    collectionGrid = tkl.TrackCollection()
    collectionFusion = tkl.TrackCollection()
    for trace in cutCollection:
        num = trace.getObsAnalyticalFeature('num', 0)
        track_id = trace.getObsAnalyticalFeature('track_id', 0)
        user_id = trace.getObsAnalyticalFeature('user_id', 0)

        if cpt%100 == 0:
            print ('   ', cpt, '/', cutCollection.size())


        trackG = trace.copy()
        trackG.resample(RESAMPLE_SIZE_GRID, mode=tkl.MODE_SPATIAL)
        trackG.uid = user_id
        trackG.tid = track_id
        trackG.createAnalyticalFeature('num', num)
        trackG.createAnalyticalFeature('track_id', track_id)
        trackG.createAnalyticalFeature('user_id', user_id)
        collectionGrid.addTrack(trackG)

        trackF = trace.copy()
        trackF.resample(RESAMPLE_SIZE_FUSION, mode=tkl.MODE_SPATIAL)
        trackF.uid = user_id
        trackF.tid = track_id
        trackF.createAnalyticalFeature('num', num)
        trackF.createAnalyticalFeature('track_id', track_id)
        trackF.createAnalyticalFeature('user_id', user_id)
        collectionFusion.addTrack(trackF)


    print ('    Nombre de traces après resampling: ' + str(collectionGrid.size()))
    print ('    Nombre de traces après resampling: ' + str(collectionFusion.size()))
    print ('Fin ré-échantillonnage.')




    # =============================================================================
    #        Enregistrement
    #
    af_names = ['num', 'track_id', 'user_id']
    
    resampledtracespath = RESPATH + 'resample_grid/'
    tkl.TrackWriter.writeToFiles(collectionGrid, resampledtracespath,
                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                 h=1, separator=";", af_names=af_names)
    resampledtracespath = RESPATH + 'resample_fusion/'
    tkl.TrackWriter.writeToFiles(collectionFusion, resampledtracespath,
                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                 h=1, separator=";", af_names=af_names)

    print ("Fin de l'enregistrement des traces ré-échantillonnées.")

    print ("Fin.")



