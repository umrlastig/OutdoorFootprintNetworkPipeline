# -*- coding: utf-8 -*-


import tracklib as tkl

from footprint2graph import logEnv
from footprint2graph import segmentation_resample, second_round
from footprint2graph import density_polygonize
from footprint2graph import addTopologyToNetwork
from footprint2graph import createNetworkGeom



def run_iteration(pipeline_idx, config, collection=None):
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

    if pipeline_idx <=0 or pipeline_idx > 10:
        print ('ERROR : variable pipeline_idx need to be integer')
        return

    print ('-------------------------------------------------------------------------------')
    print ('-------------------------------------------------------------------------------')
    print ('            ITERATION ' , pipeline_idx)
    print ('-------------------------------------------------------------------------------')
    print ('-------------------------------------------------------------------------------')

    respath = config["output"]["RESULT_PATH"]

    if pipeline_idx == 1:
        logEnv(respath)

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
    SEUIL_DENSITE = config["iterations"][0]["SEUIL_DENSITE"]
    SEUIL_SURFACE = config["iterations"][0]["SEUIL_SURFACE"]
    cut_factor    = config["iterations"][0]["CUT_FACTOR"]
    interp_dist   = config["iterations"][0]["INTERP_DIST"]
    clean_dist    = config["iterations"][0]["CLEAN_DIST"]

    density_polygonize(respath, G1_SIZE, G2_SIZE, SEUIL_DENSITE, SEUIL_SURFACE,
                       pipeline_idx,
                       cut_factor=cut_factor, interp_dist=interp_dist, clean_dist=clean_dist)

    # -------------------------------------------------------------------------
    #    STEP 2 : TOPOLOGY
    #

    SEARCH = config["iterations"][0]["CURVE_HEIGHT"]
    h      = config["iterations"][0]["CURVEH_WAVE_LENGTH"]
    
    addTopologyToNetwork(respath, SEARCH, h, pipeline_idx)


    # -------------------------------------------------------------------------
    #    STEP 3 : GEOMETRY
    #
    SEARCH = config["iterations"][0]["SEARCH"]
    BUFFER = config["iterations"][0]["BUFFER"]

    createNetworkGeom(respath, SEARCH, BUFFER, pipeline_idx)









