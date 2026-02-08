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
# Paramètre 2 : chemin/répertoire où sont stockés les traces :
#                           un fichier csv par trace

rawtracespath = r'/home/md_vandamme/4_RESEAU/ExampleTest/decoup/'



# -----------------------------------------------------------------------------
# Paramètre 3 : chemin/répertoire où sont stockés les traces :
#                           un fichier csv par trace

resampledtracespath = r'/home/md_vandamme/4_RESEAU/ExampleTest/resample/'




# =============================================================================
#         LECTURE des traces de la ZE
#

fmt = tkl.TrackFormat({'ext': 'CSV',
                       'srid': 'ENU',
                       'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                       'time_fmt': '2D/2M/4Y 2h:2m:2s',
                       'separator': ';',
                       'header': 0,
                       'cmt': '#',
                       'read_all': True})

collection2 = tkl.TrackReader.readFromFile(rawtracespath, fmt)
print ('Nb de traces lues : ', collection2.size())
print ('Fin de la lecture des données 1/3.')




# =============================================================================
#         Resampling spatial
#

print ('    Début ré-échantillonnage')

cpt = 1
collection = tkl.TrackCollection()
for trace in collection2:
    if cpt%100 == 0:
        print ('   ', cpt, '/', collection2.size())
    cpt += 1

    trace.resample(RESAMPLE_SIZE, tkl.MODE_SPATIAL)
    trace.uid = cpt
    trace.tid = cpt
    collection.addTrack(trace)


print ('    Nombre de traces après resampling: ' + str(collection.size()))
print ('Fin ré-échantillonnage 2/3.')




# =============================================================================
#         Affichage des résultats dans QGis
#

QGIS.plotTracks(collection, type='POINT',
                style=PointStyle.simpleSquareBlue,
                title='Resampled points')

tkl.TrackWriter.writeToFiles(collection, resampledtracespath,
                             id_E=1, id_N=0, id_U=3, id_T=2,
                             h=1, separator=";")

print ("Fin de l'enregistrement et de l'affichage des données dans QGIS 3/3.")


print ("END SCRIPT 1.")




