# -*- coding: utf-8 -*-


""" ======================================================================= """
"""     PARAMETRES  INPUT-OUTPUT                                            """
"""                                                                         """


""" ======================================================================= """
"""     PARAMETRES  GLOBAL                                                  """
"""                                                                         """

# Répertoire des résultats
#   créé, où les données en sortie vont être enregistrées
#   ce sera l'entrée du prochain script
#
RESPATH = r'/home/md_vandamme/4_RESEAU/ExampleZ1Walk/'


# Paramètre 3 : chemin/répertoire où sont stockés les traces Outdoorvision:
#                           un pré-traitement doit déjà avoir été fait (Cf FTP):
#                           un fichier CSV par trace

# tracespathsource = r'/home/md_vandamme/5_GPS/OV/BAUGES/run/'
tracespathsource = r'/home/md_vandamme/5_GPS/OV/BAUGES/walk/'


# Paramètre 4: Coordonnées de la zone d'étude sur laquelle on construit le réseau
#                           Polygone sous la forme d'un tableau de X et de Y

# traces de la zone 1 (1km x 1km)
#X = [949798, 950234, 951228, 951259, 950326, 950120, 950298, 949766, 949329, 949138, 949145, 949340, 949397, 949457, 949798]
#Y = [6513065, 6513079, 6512862, 6512504, 6512529, 6512224, 6511908, 6511248, 6510989, 6511152, 6511415, 6511794, 6512337, 6513104, 6513065]

# traces de la zone 1 (3km x 3km)
# 947898
X = [950987, 951409, 950696, 949467, 947934, 948545, 950987]
Y = [6513197, 6512091, 6511113, 6510719, 6511949, 6512621, 6513197]




""" ======================================================================= """
"""     PARAMETRES  TRACES                                                  """
"""                                                                         """

# Paramètre 1 : Nombre de points minimum pour un morceau de trace au moment du découpage
#               si le nombre n'est pas atteint, le morceau de trace est oublié
NB_OBS_MIN    = 10


# Paramètre 2 : Distance en mètres entre 2 points,
#               si supérieure au seuil on coupe la trace
DIST_MAX_2OBS = 50


# Paramètre 2.1 : 1 point tous les 1 mètres, avec un re-sampling spatial

RESAMPLE_SIZE = 1




""" ======================================================================= """
"""     PARAMETRES  IMAGES                                                  """
"""                                                                         """

G1_SIZE = 2
G2_SIZE = 50
SEUIL = 15


SEUIL_SURFACE = 5000 # m2

connectparam = {
    'HOST': 'localhost',
    'PORT': 5433,
    'DATABASE' : 'test',
    'USER' : 'test',
    'PASSWD' : 'test'
}


""" ======================================================================= """
"""     PARAMETRES  RESEAU                                                  """
"""                                                                         """

# Pour la construction du réseau
tolerance = 0.1    # 0.05
seuil_doublon = 0.1

# Longueur des petits arcs à supprimer
DIST_MIN_ARC = 30     # 20



""" ======================================================================= """
"""     PARAMETRES  OPERATION  MM and AGG                                   """
"""                                                                         """

# Map matching
SEARCH = 25

# Aggregation






""" ======================================================================= """
""" ======================================================================= """

# Message qui indique que les paramètres ont bien été importés
print ('Parameters imported from the configuration module.')










