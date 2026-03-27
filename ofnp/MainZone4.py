# -*- coding: utf-8 -*-

import os
import time

from source.Selection import decoup_resample
from source.Image import density_polygonize
from source.Topology import network
from source.Geometry import createNetworkGeom
from source.Refining import second_round

STAGE = 4

""" ======================================================================= """
"""     PARAMETRES  GLOBAL                                                  """
"""                                                                         """

RESPATH = r'/home/md_vandamme/4_RESEAU/Z4Walk/'
tracespathsource = r'/home/md_vandamme/5_GPS/OV/CHAM/walk/'

X = [991856, 992413, 993570, 994588, 996935, 997907, 998989, 998349, 997287,
     996091, 995323, 994575, 994153, 992598, 991856]
Y = [6543252, 6544134, 6544480, 6544876, 6544876, 6544652, 6543680, 6542612,
     6541441, 6540603, 6540616, 6540123, 6539695, 6541320, 6543252]

'''
X = [992221,995136,998122,996118,992610,992221]
Y = [6542297,6543073,6542339,6540617,6541302,6542297]
'''

""" ======================================================================= """
"""     PARAMETRES  TRACES                                                  """
"""                                                                         """

# Paramètre : Nombre de points minimum pour un morceau de trace au moment du découpage
#             si le nombre n'est pas atteint, le morceau de trace est oublié
NB_OBS_MIN           = 10

# Paramètre : Distance en mètres entre 2 points, si supérieure au seuil on coupe la trace
DIST_MAX_2OBS        = 50


""" ======================================================================= """
"""     PARAMETRES  IMAGES                                                  """
"""                                                                         """

G1_SIZE = 2
G2_SIZE = 50
SEUIL = 15
SEUIL_SURFACE = 50000 # m2




""" ======================================================================= """
"""     PARAMETRES  RESEAU                                                  """
"""                                                                         """

# Longueur des petits arcs à supprimer
DIST_MIN_ARC  = 30



""" ======================================================================= """
"""     PARAMETRES  OPERATION  MM and AGG                                   """
"""                                                                         """

# Map matching
SEARCH = 25  #30 

# Aggregation







""" ======================================================================= """
"""     Preparation de l'environnelent                                      """
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
if not os.path.exists(RESPATH + 'geometry/fusion'):
    os.makedirs(RESPATH + 'geometry/fusion')
if not os.path.exists(RESPATH + 'geometry/raccord'):
    os.makedirs(RESPATH + 'geometry/raccord')
if not os.path.exists(RESPATH + 'points_left'):
    os.makedirs(RESPATH + 'points_left')



""" ======================================================================= """
"""     Lancement des scripts                                               """
"""                                                                         """



#
# Script à lancer étape par étape de 1 à 6 pour des raisons
#        de performance : on charge dans chaque étape ce dont on a besoin
#        et de pratique : permet de régler le pipeline au fur et à mesure
#

if STAGE == 1:
    t0 = time.time()
    decoup_resample(RESPATH, tracespathsource, NB_OBS_MIN, DIST_MAX_2OBS, X, Y)
    t1 = time.time()
    total = t1-t0
    print ("Execution time (s):", total)


if STAGE == 2:
    t0 = time.time()
    density_polygonize(RESPATH, G1_SIZE, G2_SIZE, SEUIL, SEUIL_SURFACE, prefix='PT')
    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)


if STAGE == 3:
    t0 = time.time()
    network(RESPATH, DIST_MIN_ARC)
    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)


if STAGE == 4:
    t0 = time.time()
    createNetworkGeom(RESPATH, SEARCH, NB_OBS_MIN, DIST_MAX_2OBS)
    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)
