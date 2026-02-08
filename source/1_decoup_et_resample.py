# -*- coding: utf-8 -*-


import tracklib as tkl
from tracklib.util.qgis import QGIS, LineStyle, PointStyle


# =============================================================================
#     PARAMETRES  INPUT-OUTPUT
#

# -----------------------------------------------------------------------------
# Paramètre 1 : 1 point tous les 1 mètres, avec un re-sampling spatial

RESAMPLE_SIZE = 1

# -----------------------------------------------------------------------------
# Paramètre 2 : Nombre de points minimum pour une trace au moment du découpage

NB_OBS_MIN    = 10

# -----------------------------------------------------------------------------
# paramètre 3 : Distance en mètres entre 2 points,
#               si supérieure au seuil on coupe la trace

DIST_MAX_2OBS = 50


# -----------------------------------------------------------------------------
# Paramètre 4 : chemin/répertoire où sont stockés les traces :
#                           un fichier csv par trace

# tracescsvpath = r'/home/md_vandamme/5_GPS/OV/BAUGES/run/'
tracescsvpath = r'/home/md_vandamme/5_GPS/OV/BAUGES/walk/'


# -----------------------------------------------------------------------------
# Paramètre 5: Coordonnées de la zone d'étude sous la forme d'un tableau de X et de Y

# traces de la zone 1
X = [945878, 956330, 955879, 954402, 952511, 950389, 948774, 945857, 945878]
Y = [6516870, 6516805, 6508417, 6506849, 6506503, 6505649, 6504150, 6503762, 6516870]

# traces sur un petit extrait de la zone 1 (1km x 1km)
# X = [949798, 950234, 951228, 951259, 950326, 950120, 950298, 949766, 949329, 949138, 949145, 949340, 949397, 949457, 949798]
# Y = [6513065, 6513079, 6512862, 6512504, 6512529, 6512224, 6511908, 6511248, 6510989, 6511152, 6511415, 6511794, 6512337, 6513104, 6513065]


# -----------------------------------------------------------------------------
# Paramètre 6 : répertoire créé, où les données en sortie vont être enregistrées
#               c'est l'entrée du prochain script
#
tracespath = r'/home/md_vandamme/4_RESEAU/ExampleRunning/traces/'




# =============================================================================
#         LECTURE de toutes les traces
#

fmt = tkl.TrackFormat({'ext': 'CSV',
                       'srid': 'ENU',
                       'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                       'time_fmt': '2D/2M/4Y 2h:2m:2s',
                       'separator': ';',
                       'header': 0,
                       'cmt': '#',
                       'read_all': True})

collection2 = tkl.TrackReader.readFromFile(tracescsvpath, fmt)
print ('Fin de la lecture des données 1/4.')



# =============================================================================
#         Découpage
#

print ('    Début découpage.')

poly = tkl.Polygon(X, Y)
constraintBBox = tkl.Constraint(shape=poly,
                                mode=tkl.MODE_CROSSES,
                                type=tkl.TYPE_CUT_AND_SELECT)

# On prépare la nouvelle collection de traces
cpt = 1
collection3 = tkl.TrackCollection()
for trace in collection2:

    if cpt%200 == 0:
        print ('    ', cpt, '/', collection2.size())
    cpt += 1
    
    selection = constraintBBox.select(tkl.TrackCollection([trace]))
    if len(selection) <= 0:
        continue

    o1 = None
    tn = tkl.Track()
    for o2 in selection.getTrack(0):
        if o1 is not None:
            if o1.distance2DTo(o2) > DIST_MAX_2OBS:
                # on coupe la trace
                if tn.size() >= NB_OBS_MIN:
                    tn.uid = trace.tid
                    tn.tid = trace.tid
                    collection3.addTrack(tn)
                tn = tkl.Track()
        tn.addObs(o2)
        o1 = o2

    # dernière trace
    if tn.size() >= NB_OBS_MIN:
        collection3.addTrack(tn)


print ('    Nombre de traces après découpage : ' + str(collection3.size()))
print ('Fin découpage 2/4.')




# =============================================================================
#         Resampling spatial
#

print ('    Début ré-échantillonnage')

cpt = 1
collection = tkl.TrackCollection()
for trace in collection3:
    if cpt%100 == 0:
        print ('    ', cpt, '/', collection3.size())
    cpt += 1

    track = trace.copy()
    track.resample(RESAMPLE_SIZE, tkl.MODE_SPATIAL)
    track.uid = cpt
    track.tid = cpt
    collection.addTrack(track)

print ('    Nombre de traces après resampling: ' + str(collection.size()))

tkl.TrackWriter.writeToFiles(collection, tracespath,
                             id_E=1, id_N=0, id_U=3, id_T=2,
                             h=1, separator=";")

print ('Fin ré-échantillonnage 3/4.')




# =============================================================================
#         Affichage des résultats dans QGis
#

QGIS.plotTracks(collection, type='LINE',
                style=LineStyle.simpleBlue,
                title='Traces ré-échantillonnées et découpées')
QGIS.plotTracks(collection, type='POINT',
                title='Traces ré-échantillonnées et découpées')


print ("Fin de l'affichage des données dans QGIS 4/4.")


print ("END SCRIPT 1.")




