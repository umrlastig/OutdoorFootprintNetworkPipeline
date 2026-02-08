# -*- coding: utf-8 -*-


import matplotlib.pyplot as plt
import tracklib as tkl
from tracklib.util.qgis import QGIS, LineStyle, PointStyle


# =============================================================================
#       INPUT - OUTPUT
#

# données en entrée
RESAMPLE_SIZE = 1
NB_OBS_MIN    = 10 # nombre de points minimum pour une trace
DIST_MAX_2OBS = 50 # si supérieur on coupe la trace
tracescsvpath = r'/home/md_vandamme/5_GPS/OV/BAUGES/run/'

X = [945878, 956330, 955879, 954402, 952511, 950389, 948774, 945857, 945878]
Y = [6516870, 6516805, 6508417, 6506849, 6506503, 6505649, 6504150, 6503762, 6516870]

# X = [949798, 950234, 951228, 951259, 950326, 950120, 950298, 949766, 949329, 949138, 949145, 949340, 949397, 949457, 949798]
# Y = [6513065, 6513079, 6512862, 6512504, 6512529, 6512224, 6511908, 6511248, 6510989, 6511152, 6511415, 6511794, 6512337, 6513104, 6513065]

# données en sortie
# Le répertoire doit être créé
tracespath = r'/home/md_vandamme/4_RESEAU/ExampleRunning/traces/'


# =============================================================================
#         LECTURE de toutes les traces
#
poly = tkl.Polygon(X, Y)
constraintBBox = tkl.Constraint(shape=poly,
                                mode=tkl.MODE_CROSSES,
                                type=tkl.TYPE_CUT_AND_SELECT)

fmt = tkl.TrackFormat({'ext': 'CSV',
                       'srid': 'ENU',
                       'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                       'time_fmt': '2D/2M/4Y 2h:2m:2s',
                       'separator': ';',
                       'header': 0,
                       'cmt': '#',
                       'read_all': True})

collection2 = tkl.TrackReader.readFromFile(tracescsvpath, fmt)
print ('Fin de la lecture des données 1/2.')


# =============================================================================
#         Découpage et ré-échantillonnage
#

print ('Début découpage et ré-échantillonnage')

# On prépare la nouvelle collection de traces
cpt = 1
collection = tkl.TrackCollection()
for trace in collection2:
    
    trace.resample(RESAMPLE_SIZE, tkl.MODE_SPATIAL)

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
                    collection.addTrack(tn)
                tn = tkl.Track()
        tn.addObs(o2)
        o1 = o2

    # dernière trace
    if tn.size() >= NB_OBS_MIN:
        collection.addTrack(tn)

    if cpt%100 == 0:
        print ('    ', cpt, '/', collection2.size())
    cpt += 1


print ('Number of tracks in zone1: ' + str(collection.size()))


tkl.TrackWriter.writeToFiles(collection, tracespath,
                             id_E=1, id_N=0, id_U=3, id_T=2,
                             h=1, separator=";")

print ('Fin découpage et ré-échantillonnage 2/3.')



# =============================================================================
#         Affichage des résultats dans QGis
#

QGIS.plotTracks(collection, type='LINE',
                style=LineStyle.simpleBlue,
                title='Traces ré-échantillonnées et découpées')
QGIS.plotTracks(collection, type='POINT',
                title='Traces ré-échantillonnées et découpées')


print ("Fin de l'affichage des données 3/3.")


print ("END script 1.")




