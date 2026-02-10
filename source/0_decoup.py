# -*- coding: utf-8 -*-


import tracklib as tkl
from tracklib.util.qgis import QGIS, LineStyle, PointStyle


""" ======================================================================= """
"""     PARAMETRES  INPUT-OUTPUT                                            """
"""                                                                         """

# -----------------------------------------------------------------------------
# Paramètre 1 : Nombre de points minimum pour un morceau de trace au moment du découpage
#               si le nombre n'est pas atteint, le morceau de trace est oublié

NB_OBS_MIN    = 10


# -----------------------------------------------------------------------------
# Paramètre 2 : Distance en mètres entre 2 points,
#               si supérieure au seuil on coupe la trace

DIST_MAX_2OBS = 50


# -----------------------------------------------------------------------------
# Paramètre 3 : chemin/répertoire où sont stockés les traces Outdoorvision:
#                           un pré-traitement doit déjà avoir été fait (Cf FTP):
#                           un fichier CSV par trace

# tracespathsource = r'/home/md_vandamme/5_GPS/OV/BAUGES/run/'
tracespathsource = r'/home/md_vandamme/5_GPS/OV/BAUGES/walk/'


# -----------------------------------------------------------------------------
# Paramètre 4: Coordonnées de la zone d'étude sur laquelle on construit le réseau
#                           Polygone sous la forme d'un tableau de X et de Y

# traces de la zone 1 (1km x 1km)
X = [949798, 950234, 951228, 951259, 950326, 950120, 950298, 949766, 949329, 949138, 949145, 949340, 949397, 949457, 949798]
Y = [6513065, 6513079, 6512862, 6512504, 6512529, 6512224, 6511908, 6511248, 6510989, 6511152, 6511415, 6511794, 6512337, 6513104, 6513065]


# -----------------------------------------------------------------------------
# Paramètre 5 : répertoire créé, où les données en sortie vont être enregistrées
#               ce sera l'entrée du prochain script
#

tracespath = r'/home/md_vandamme/4_RESEAU/ExampleTest/decoup/'



""" ======================================================================= """
"""         LECTURE de toutes les traces                                    """
"""                                                                         """

fmt = tkl.TrackFormat({'ext': 'CSV',
                       'srid': 'ENU',
                       'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
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
tkl.TrackWriter.writeToFiles(collection, tracespath,
                             id_E=1, id_N=0, id_U=3, id_T=2,
                             h=1, separator=";", af_names=af_names)

print ("Fin de l'enregistrement et affichage des données dans QGIS 3/3.")



""" ======================================================================= """
"""           FIN                                                           """
"""                                                                         """
print ("END SCRIPT 0.")




