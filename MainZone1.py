# -*- coding: utf-8 -*-

import time

from Param import *
from source.Selection import decoup, resample
from source.Image import density, polygonize
from source.Topology import network
from source.Mapmatch import mapmatch
from source.Aggregation import aggregation


# Polygon ((950987 6513197, 951409 6512091, 950696 6511113, 949467 6510719,
#           947898 6511949, 948545 6512621, 950987 6513197))


#
# Script à lancer étape par étape de 1 à 6 pour des raisons
#        de performance : on charge dans chaque étape ce dont on a besoin
#        et de pratique : permet de régler le pipeline au fur et à mesure
#
#   1 : Lecture traces brutes, découpage, affichage dans QGis
#   2 : Lecture traces découpées, resampling spatial, affichage dans QGis
#   3 : Lecture traces ré-échantillonnées et découpées, création des cartes
#   4 : Lecture des cartes, Filtre morphologique, Vectorisation,
#                      Squeletisation : center line dans Postgis
#       Connection à Postgis
#   5 :
#
#
STAGE = 7


if STAGE == 1:
    t0 = time.time()
    decoup(tracespathsource, NB_OBS_MIN, DIST_MAX_2OBS, X, Y, RESPATH)
    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)
if STAGE == 2:
    t0 = time.time()
    resample(RESPATH, RESAMPLE_SIZE)
    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)
if STAGE == 3:
    t0 = time.time()
    density(RESPATH, G1_SIZE, G2_SIZE, SEUIL)
    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)
if STAGE == 4:
    t0 = time.time()
    polygonize(RESPATH, SEUIL_SURFACE, connectparam)
    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)
if STAGE == 5:
    t0 = time.time()
    network(RESPATH, tolerance, seuil_doublon, DIST_MIN_ARC)
    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)
if STAGE == 6:
    t0 = time.time()
    mapmatch(RESPATH, SEARCH, DIST_MAX_2OBS, NB_OBS_MIN)
    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)
if STAGE == 7:
    t0 = time.time()
    aggregation(RESPATH, SEARCH)
    t1 = time.time()
    total = t1-t0
    print ("Temps d'exécution en s:", total)


