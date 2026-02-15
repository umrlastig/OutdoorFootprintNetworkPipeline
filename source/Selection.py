# -*- coding: utf-8 -*-

import tracklib as tkl
from tracklib.util.qgis import QGIS, LineStyle, PointStyle


def decoup(tracespathsource, NB_OBS_MIN, DIST_MAX_2OBS, X, Y, RESPATH):

    print ("Lancement du découpage...")

    """ ======================================================================= """
    """         LECTURE de toutes les traces                                    """
    """                                                                         """
    
    fmt = tkl.TrackFormat({'ext': 'CSV',
                           'srid': 'ENU',
                           'id_E': 1, 'id_N': 0, 'id_U': 3, 'id_T': 2,
                           'time_fmt': '2D/2M/4Y 2h:2m:2s',
                           'separator': ';',
                           'header': 0,
                           'cmt': '#',
                           'read_all': True})
    collection2 = tkl.TrackReader.readFromFile(tracespathsource, fmt)
    print ('Fin de la lecture des données 1/3.')



    """ ======================================================================= """
    """         Découpage                                                       """
    """                                                                         """
    
    print ('    Début découpage.')
    
    poly = tkl.Polygon(X, Y)
    constraintBBox = tkl.Constraint(shape=poly,
                                    mode=tkl.MODE_CROSSES,
                                    type=tkl.TYPE_CUT_AND_SELECT)

    # On prépare la nouvelle collection de traces
    cpt = 1
    collection = tkl.TrackCollection()
    for trace in collection2:
    
        if cpt%200 == 0:
            print ('   ', cpt, '/', collection2.size())
        cpt += 1
    
        selection = constraintBBox.select(tkl.TrackCollection([trace]))
        if len(selection) <= 0:
            continue
    
        cpttrace = 1
    
        o1 = None
        tn = tkl.Track()
        for o2 in selection.getTrack(0):
            if o1 is not None:
                if o1.distance2DTo(o2) > DIST_MAX_2OBS:
                    # on coupe la trace pour créer un nouveau morceau
                    if tn.size() >= NB_OBS_MIN:
                        tn.uid = str(trace.tid) + "-" + str(cpttrace)
                        tn.tid = str(trace.tid) + "-" + str(cpttrace)
                        tn.createAnalyticalFeature('num', trace.getObsAnalyticalFeature('num', 0))
                        tn.createAnalyticalFeature('track_id', tn.tid)
                        tn.createAnalyticalFeature('user_id', tn.uid)
    
                        cpttrace += 1
                        collection.addTrack(tn)
                    tn = tkl.Track()
            tn.addObs(o2)
            o1 = o2
    
        # dernier morceau de trace
        if tn.size() >= NB_OBS_MIN:
            tn.uid = str(trace.tid) + "-" + str(cpttrace)
            tn.tid = str(trace.tid) + "-" + str(cpttrace)
            tn.createAnalyticalFeature('num', trace.getObsAnalyticalFeature('num', 0))
            tn.createAnalyticalFeature('track_id', tn.tid)
            tn.createAnalyticalFeature('user_id', tn.uid)
            cpttrace += 1
            collection.addTrack(tn)
    
    
    print ('    Nombre de traces après découpage : ' + str(collection.size()))
    print ('Fin découpage 2/3.')
    
    
    
    """ ======================================================================= """
    """         Affichage des résultats dans QGis                               """
    """                                                                         """
    
    QGIS.plotTracks(collection, type='LINE',
                    style=LineStyle.simpleBlue,
                    title='Raw lines')
    QGIS.plotTracks(collection, type='POINT',
                    style=PointStyle.simpleSquareBlue,
                    title='Raw points')
    
    af_names = ['num', 'track_id', 'user_id']
    tracespath = RESPATH + "decoup/"
    tkl.TrackWriter.writeToFiles(collection, tracespath,
                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                 h=1, separator=";", af_names=af_names)
    
    print ("Fin de l'enregistrement et affichage des données dans QGIS 3/3.")
    
    
    
    """ ======================================================================= """
    """           FIN                                                           """
    """                                                                         """
    print ("END SCRIPT 1.")



def resample(RESPATH, RESAMPLE_SIZE):

    print ("Lancement du resample.")


    # =============================================================================
    #         LECTURE des traces de la ZE
    #

    fmt = tkl.TrackFormat({'ext': 'CSV',
                           'srid': 'ENU',
                           'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                           'time_fmt': '2D/2M/4Y 2h:2m:2s',
                           'separator': ';',
                           'header': 0,
                           'cmt': '#',
                           'read_all': True})
    rawtracespath = RESPATH + "decoup/"
    collection2 = tkl.TrackReader.readFromFile(rawtracespath, fmt)
    print ('Nb de traces lues : ', collection2.size())
    print ('Fin de la lecture des données 1/3.')




    # =============================================================================
    #         Resampling spatial
    #

    print ('    Début ré-échantillonnage')

    cpt = 1
    collection = tkl.TrackCollection()
    for trace in collection2:
        num = trace.getObsAnalyticalFeature('num', 0)
        track_id = trace.getObsAnalyticalFeature('track_id', 0)
        user_id = trace.getObsAnalyticalFeature('user_id', 0)
        if cpt%100 == 0:
            print ('   ', cpt, '/', collection2.size())
        cpt += 1

        trace.resample(RESAMPLE_SIZE, tkl.MODE_SPATIAL)
        trace.uid = cpt
        trace.tid = cpt
        trace.createAnalyticalFeature('num', num)
        trace.createAnalyticalFeature('track_id', track_id)
        trace.createAnalyticalFeature('user_id', user_id)
        collection.addTrack(trace)


    print ('    Nombre de traces après resampling: ' + str(collection.size()))
    print ('Fin ré-échantillonnage 2/3.')




    # =============================================================================
    #         Affichage des résultats dans QGis
    #

    QGIS.plotTracks(collection, type='POINT',
                    style=PointStyle.simpleSquareBlue,
                    title='Resampled points')

    af_names = ['num', 'track_id', 'user_id']
    resampledtracespath = RESPATH + 'resample/'
    tkl.TrackWriter.writeToFiles(collection, resampledtracespath,
                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                 h=1, separator=";", af_names=af_names)

    print ("Fin de l'enregistrement et de l'affichage des données dans QGIS 3/3.")


    print ("END SCRIPT 1.")
