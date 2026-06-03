# -*- coding: utf-8 -*-


import tracklib as tkl

from footprint2graph import logEnv
from footprint2graph import segmentation_resample, second_round
from footprint2graph import density_polygonize
from footprint2graph import addTopologyToNetwork
from footprint2graph import createNetworkGeom


# Paramètre : Nombre de points minimum pour un morceau de trace au moment du découpage
#             si le nombre n'est pas atteint, le morceau de trace est oublié
NB_OBS_MIN           = 10 # il faudrait qu'une trace fasse au moins 50m


# Paramètre : Distance en mètres entre 2 points,
#             si supérieure au seuil on coupe la trace
DIST_MAX_2OBS        = 50


# Pour des raisons logistiques, on sur-échantillone la trace :
#   - 1m pour le traitement d'images
#   - 5m pour la fusion
RESAMPLE_SIZE_GRID   = 1
RESAMPLE_SIZE_FUSION = 5


# Définition des grilles géométrique et contraste
G1_SIZE              = 2
G2_SIZE              = 30



def run_iteration(pipeline_idx, respath, collection=None):
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
    if collection is not None and pipeline_idx == 1:
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
    '''
    SEUIL_DENSITE = 25    # 20-24-34 - 450 - 360 - 500 - 280 - 15 - 1000
    SEUIL_SURFACE = 1000  # m2 - 50000 - 7000
    cut_factor    = 5
    interp_dist   = 5
    clean_dist    = 0
    '''
    SEUIL_DENSITE = 40    # 20-24-34 - 450 - 360 - 500 - 280 - 15 - 1000
    SEUIL_SURFACE = 200   # m2 - 50000 - 7000
    cut_factor    = 5
    interp_dist   = 5
    clean_dist    = 0
    density_polygonize(respath, G1_SIZE, G2_SIZE, SEUIL_DENSITE, SEUIL_SURFACE,
                       pipeline_idx,
                       cut_factor=cut_factor, interp_dist=interp_dist, clean_dist=clean_dist)

    # -------------------------------------------------------------------------
    #    STEP 2 : TOPOLOGY
    #
    '''
    SEARCH = 25 # 50
    h      = 5  # 10
    '''
    SEARCH = 25
    h = 10
    addTopologyToNetwork(respath, SEARCH, h, pipeline_idx)


    # -------------------------------------------------------------------------
    #    STEP 3 : GEOMETRY
    #
    '''
    SEARCH = 50 # 20
    BUFFER = 20 # 15
    '''
    SEARCH = 50
    BUFFER = 10
    createNetworkGeom(respath, SEARCH, BUFFER, pipeline_idx)









