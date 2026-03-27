# -*- coding: utf-8 -*-


import os


def setupenv(RESPATH):
    """ ======================================================================= """
    """     Preparation de l'environnement                                      """
    """   - création des répertoires si nécessaire                                                                      """
    """                                                                         """

    if not os.path.exists(RESPATH + 'decoup'):
        os.makedirs(RESPATH + 'decoup')
    if not os.path.exists(RESPATH + 'geometry'):
        os.makedirs(RESPATH + 'geometry')
    if not os.path.exists(RESPATH + 'image'):
        os.makedirs(RESPATH + 'image')
    if not os.path.exists(RESPATH + 'mapmatch'):
        os.makedirs(RESPATH + 'mapmatch')
    if not os.path.exists(RESPATH + 'network'):
        os.makedirs(RESPATH + 'network')
    if not os.path.exists(RESPATH + 'resample_grid'):
        os.makedirs(RESPATH + 'resample_grid')
    if not os.path.exists(RESPATH + 'resample_fusion'):
        os.makedirs(RESPATH + 'resample_fusion')
    if not os.path.exists(RESPATH + 'mapmatch/tmm'):
        os.makedirs(RESPATH + 'mapmatch/tmm')
    if not os.path.exists(RESPATH + 'mapmatch/tmm1'):
        os.makedirs(RESPATH + 'mapmatch/tmm1')
        if not os.path.exists(RESPATH + 'mapmatch/tmm2'):
            os.makedirs(RESPATH + 'mapmatch/tmm2')

    if not os.path.exists(RESPATH + 'geometry/fusion'):
        os.makedirs(RESPATH + 'geometry/fusion')
    if not os.path.exists(RESPATH + 'geometry/fusion1'):
        os.makedirs(RESPATH + 'geometry/fusion1')
    if not os.path.exists(RESPATH + 'geometry/fusion2'):
        os.makedirs(RESPATH + 'geometry/fusion2')

    if not os.path.exists(RESPATH + 'geometry/raccord'):
        os.makedirs(RESPATH + 'geometry/raccord')
    if not os.path.exists(RESPATH + 'geometry/raccord1'):
        os.makedirs(RESPATH + 'geometry/raccord1')
    if not os.path.exists(RESPATH + 'geometry/raccord2'):
        os.makedirs(RESPATH + 'geometry/raccord2')

    if not os.path.exists(RESPATH + 'points_not_mm_1'):
        os.makedirs(RESPATH + 'points_not_mm_1')
    if not os.path.exists(RESPATH + 'points_not_mm_2'):
        os.makedirs(RESPATH + 'points_not_mm_2')

