# -*- coding: utf-8 -*-


import tracklib as tkl


from footprint2graph import prepareEnv, setupEnv, logEnv
from footprint2graph import segmentation_resample, second_round
from footprint2graph import density_polygonize
from footprint2graph import addTopologyToNetwork
from footprint2graph import createNetworkGeom
from footprint2graph import mergeNetwork



def run_iteration(pipeline_idx, config, collection=None, log_level='ERROR'):
    '''
    En entrée une collection de traces avec un TID

    Parameters
    ----------
    pipeline_idx : TYPE
        DESCRIPTION.
    respath : TYPE
        DESCRIPTION.
    collection : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''

    if not isinstance(pipeline_idx, int):
        print ('ERROR : variable pipeline_idx need to be integer')
        return

    if pipeline_idx <= 0 or pipeline_idx > 10:
        print ('ERROR : variable pipeline_idx need to be integer')
        return

    print ('-----------------------------------------------------------------')
    print ('-----------------------------------------------------------------')
    print ('              ITERATION ' , pipeline_idx)
    print ('-----------------------------------------------------------------')
    print ('-----------------------------------------------------------------')

    respath = config["output"]["RESULT_PATH"]

    if collection is not None and pipeline_idx == 1:
        # Cas du début
        prepareEnv(config['output']['RESULT_PATH'])
    if pipeline_idx == 1:
        logEnv(respath)


    # prépare les répertoires pour les enregistrements
    if pipeline_idx >= 1:
        setupEnv(respath, pipeline_idx)

    #  On définit un format pour le stockage des traces modifiées dans le pipeline
    fmt = tkl.TrackFormat({'ext': 'CSV',
                       'srid': 'ENU',
                       'id_E': 1, 'id_N': 0, 'id_U': 3, 'id_T': 2,
                       'time_fmt': '2D/2M/4Y 2h:2m:2s',
                       'separator': ';',
                       'header': 0,
                       'cmt': '#',
                       'read_all': True})

    # -------------------------------------------------------------------------
    #    PREPARE COLLECTION
    #
    #  uniquement pour la première itération
    #

    NB_OBS_MIN           = config['graph_construction']['NB_OBS_MIN']
    DIST_MAX_2OBS        = config['graph_construction']['DIST_MAX_2OBS']
    RESAMPLE_SIZE_GRID   = config['graph_construction']['RESAMPLE_SIZE_GRID']

    if collection is not None and pipeline_idx == 1:
        RESAMPLE_SIZE_FUSION = config['graph_construction']['RESAMPLE_SIZE_FUSION']
        segmentation_resample(respath, collection, fmt, NB_OBS_MIN, DIST_MAX_2OBS,
                    RESAMPLE_SIZE_GRID, RESAMPLE_SIZE_FUSION)

    #
    #  uniquement pour les itérations 2 et plus
    #
    if pipeline_idx > 1:
        second_round(respath, pipeline_idx, NB_OBS_MIN, DIST_MAX_2OBS, RESAMPLE_SIZE_GRID)


    # -------------------------------------------------------------------------
    #    STEP 1 : IMAGE
    #
    G1_SIZE       = config["graph_construction"]["G1_SIZE"]
    G2_SIZE       = config["graph_construction"]["G2_SIZE"]
    SEUIL_DENSITE = config["iterations"][pipeline_idx-1]["SEUIL_DENSITE"]
    SEUIL_SURFACE = config["iterations"][pipeline_idx-1]["SEUIL_SURFACE"]
    #cut_factor    = config["iterations"][pipeline_idx-1]["CUT_FACTOR"]
    #interp_dist   = config["iterations"][pipeline_idx-1]["INTERP_DIST"]
    #clean_dist    = config["iterations"][pipeline_idx-1]["CLEAN_DIST"]

    density_polygonize(respath, G1_SIZE, G2_SIZE, SEUIL_DENSITE, SEUIL_SURFACE,
                       pipeline_idx)


    # -------------------------------------------------------------------------
    #    STEP 2 : TOPOLOGY
    #
    RESAMPLE_SIZE_FUSION = config['graph_construction']['RESAMPLE_SIZE_FUSION']
    SEARCH = config["iterations"][pipeline_idx-1]["CURVE_HEIGHT"]
    h      = config["iterations"][pipeline_idx-1]["CURVE_WAVE_LENGTH"]
    
    addTopologyToNetwork(respath, SEARCH, h, NB_OBS_MIN, RESAMPLE_SIZE_FUSION, pipeline_idx)

    # -------------------------------------------------------------------------
    #    STEP 3 : GEOMETRY
    #
    SEARCH = config["iterations"][pipeline_idx-1]["SEARCH"]
    BUFFER = config["iterations"][pipeline_idx-1]["BUFFER"]

    createNetworkGeom(respath, SEARCH, BUFFER, pipeline_idx)

    # -------------------------------------------------------------------------
    #    STEP 4 :  FUSION RESULTS
    #
    PPV_SEUIL = 20
    ELASTIC_COV_DISTANCE = 20
    EXTENSION = 50

    if pipeline_idx > 1:
        mergeNetwork(respath, pipeline_idx, PPV_SEUIL, ELASTIC_COV_DISTANCE, EXTENSION,
                     RESAMPLE_SIZE_FUSION)


    
def footprint2grap(config, collection, log_level='ERROR'):
    '''
    '''
    NBITER = int(config['graph_construction']['NUM_ITERATIONS'])
    for idx in range(0, NBITER):
        iteration_index = int(idx) + 1

        # run pipeline for the ith iteration
        run_iteration(iteration_index, config, collection, log_level)

    print ('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print ('`````````````````````````````````````````````````````````````````````')
    print ('                           FIN                                       ')
    print ('’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’’')
    print ('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')


