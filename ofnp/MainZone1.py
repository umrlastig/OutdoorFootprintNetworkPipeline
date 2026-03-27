# -*- coding: utf-8 -*-


import time

from source.Selection import decoup_resample, second_round
from source.Image import density_polygonize
from source.Topology import network
from source.Geometry import createNetworkGeom
from util.config import setupenv


STAGE = 5


""" ======================================================================= """
"""     PARAMETRES  GLOBAL                                                  """
"""                                                                         """

# Répertoire des résultats où les données en sortie vont être enregistrées
#    ces données servent comme entrée dans l'étape suivante
#
#RESPATH = r'/home/md_vandamme/4_RESEAU/Ex2Z1Run/'
RESPATH = r'/home/md_vandamme/4_RESEAU/Ex2Z1Walk/'
#RESPATH = r'/home/md_vandamme/4_RESEAU/Ex3Z1Run/'
#RESPATH = r'/home/md_vandamme/4_RESEAU/DixTracesTest/'


# Paramètre : chemin/répertoire où sont stockés les traces Outdoorvision:
#                           un pré-traitement doit déjà avoir été fait (Cf FTP):
#                           un fichier CSV par trace
#tracespathsource = r'/home/md_vandamme/5_GPS/OV/BAUGES/run/'
tracespathsource = r'/home/md_vandamme/5_GPS/OV/BAUGES/walk/'
#tracespathsource = r'/home/md_vandamme/4_RESEAU/GPS10/tracks/'


# Paramètre : Coordonnées de la zone d'étude sur laquelle on construit le réseau
#                           Polygone sous la forme d'un tableau de X et de Y

# traces de la zone 1 (1km x 1km)
#X = [949798, 950234, 951228, 951259, 950326, 950120, 950298, 949766, 949329, 949138, 949145, 949340, 949397, 949457, 949798]
#Y = [6513065, 6513079, 6512862, 6512504, 6512529, 6512224, 6511908, 6511248, 6510989, 6511152, 6511415, 6511794, 6512337, 6513104, 6513065]

# traces de la zone 1 (3km x 3km)
# POLYGON ((950987 6513197, 951409 6512091, 950696 6511113, 949467 6510719, 947934 6511949, 948545 6512621, 950987 6513197))
X = [950987, 951409, 950696, 949467, 947934, 948545, 950987]
Y = [6513197, 6512091, 6511113, 6510719, 6511949, 6512621, 6513197]



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

RESAMPLE_SIZE_GRID = 1

G1_SIZE = 2
G2_SIZE = 30 # 50

SEUIL_DENSITE = 360  # 15 - 1000
SEUIL_SURFACE = 1000 # m2 - 50000 - 7000

r = 2   # Raster resolution
f = 2   # Cut factor


""" ======================================================================= """
"""     PARAMETRES  RESEAU                                                  """
"""                                                                         """

# Longueur des petits arcs à supprimer
# 30
DIST_MIN_ARC  = 50



""" ======================================================================= """
"""     PARAMETRES  OPERATION  MM and AGG                                   """
"""                                                                         """

# Map matching
RESAMPLE_SIZE_FUSION = 5
SEARCH = 25

# Agrégation



""" ======================================================================= """
"""     Préparation de l'environnement                                      """
""" ======================================================================= """

setupenv(RESPATH)






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
    decoup_resample(RESPATH, tracespathsource, X, Y,
                    NB_OBS_MIN, DIST_MAX_2OBS,
                    RESAMPLE_SIZE_GRID, RESAMPLE_SIZE_FUSION)
    t1 = time.time()
    total = t1-t0
    print ("Execution time (s):", total)


if STAGE == 2:
    density_polygonize(RESPATH, G1_SIZE, G2_SIZE, SEUIL_DENSITE, SEUIL_SURFACE,
                       prefix='PT', rep='resample_grid', f=2)



if STAGE == 3:
    network(RESPATH, DIST_MIN_ARC)



if STAGE == 4:
    createNetworkGeom(RESPATH, SEARCH, NB_OBS_MIN, DIST_MAX_2OBS)



if STAGE == 5:
    t0 = time.time()

    rep='points_not_mm_1'

    SEUIL_DENSITE = 14
    SEUIL_SURFACE = 500

    second_round(RESPATH, NB_OBS_MIN, DIST_MAX_2OBS, RESAMPLE_SIZE_GRID, rep)
    
    density_polygonize(RESPATH, G1_SIZE, G2_SIZE, SEUIL_DENSITE, SEUIL_SURFACE,
                        prefix='ST', rep=rep)

    '''
    network(RESPATH, DIST_MIN_ARC, prefix='ST')

    createNetworkGeom(RESPATH, SEARCH, NB_OBS_MIN, DIST_MAX_2OBS, prefix='ST',
                      pathtraces='points_not_mm_1', pathtmm='tmm1',
                      pathfusion='fusion1', pathraccord='raccord1')
    '''
    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)



if STAGE == 6:
    t0 = time.time()

    SEUIL = 14
    SEUIL_SURFACE = 500

    second_round(RESPATH, NB_OBS_MIN, DIST_MAX_2OBS, RESAMPLE_SIZE_GRID,
                 rep='points_not_mm_2', pathtmm='tmm1')

    density_polygonize(RESPATH, G1_SIZE, G2_SIZE, SEUIL, SEUIL_SURFACE,
                        prefix='TT', rep='points_not_mm_2')

    #network(RESPATH, DIST_MIN_ARC, prefix='TT')
    #
    #createNetworkGeom(RESPATH, SEARCH, NB_OBS_MIN, DIST_MAX_2OBS, prefix='ST',
    #                  pathtraces='points_not_mm_2', pathtmm='tmm2',
    #                  pathfusion='fusion2', pathraccord='raccord2')

    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)










