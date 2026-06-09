# -*- coding: utf-8 -*-


import time
import datetime
import json
import os



def log_event(RESPATH, event):
    path = RESPATH
    with open(path, "w") as f:
        f.write(json.dumps(event) + "\n")



def report_file(RESPATH, file):
    print ('=================================================================')
    print ('                  PIPELINE REPORT INFORMATION                    ')
    print ('')

    pathfile = os.path.join(RESPATH, file)
    with open(pathfile) as f:
        d = json.load(f)


    if file[0:8] == "mapmatch":
        idxiter = int(file[8:9])
        _mapmatch(d, idxiter)
    elif file[0:8] == "conflate":
        idxiter = int(file[8:9])
        _conflate(d, idxiter)
    elif file[0:9] == "aggregate":
        idxiter = int(file[9:10])
        _aggregate(d, idxiter)
    elif file[0:9] == "candidate":
        idxiter = int(file[9:10])
        _candidate(d, idxiter)

    elif file[0:3] == "env":
        _env(d)
    elif file[0:7] == "rawdata":
        _rawdata(d)

    elif file[0:8] == "topology":
        idxiter = int(file[8:9])
        _topology(d, idxiter)
    elif file[0:5] == "image":
        idxiter = int(file[5:6])
        _image(d, idxiter)

    else:
        # print (file[0:8], file[8:9])
        print ('Erreur : nom du fichier inconnu.')



def _mapmatch(d, idxiter):

    print ('Map Matching ')
    print ("    Itération n° :", idxiter)
    print ('    Fin du traitement :', datetime.datetime.fromtimestamp(d['ts']).strftime('%d/%m/%Y %H:%M:%S'))
    print ('')

    # print ('--------------------------------------------------')
    print ('Search radius (m):               ', d['Search radius (m)'])
    print ('')

    print ('Results')
    print ('--------------------------------------------------')
    print ('Map-matched points:              ', d['Number of map-matched points'], "(", d['Percentage of map-matched points (%)'], '% )')
    print ('Off-track points:                ', d['Number of off-track points'], "(", d['Percentage of off_track points (%)'], '% )')

    print ('')
    print ('Quality')
    print ('--------------------------------------------------')
    print ('Root Mean Square Error (RMSE) :  ', d['Root Mean Square Error (m)'], "m")
    print ('Maximal displacement :           ', round(d['Maximal displacement (m)'], 2), "m")
    print ('')


def _conflate(d, idxiter):

    print ('Conflation de la géométrie du réseau sur le squelette')
    print ("    Itération n° :", idxiter)
    print ('    Fin du traitement :', datetime.datetime.fromtimestamp(d['ts']).strftime('%d/%m/%Y %H:%M:%S'))
    print ('')

    print ('Results')
    print ('--------------------------------------------------')
    print ('Segments conflated :            ', d['Number of conflated segments'], "(", d['Percent of conflated segments'], "% )")
    print ('')

    print ('Distorsion')
    print ('--------------------------------------------------')
    print ('Total distorsion RMSE :         ', round(d['Total distorsion RMSE (m)'], 3), 'm')
    print ('Maximum distorsion RMSE :       ', round(d['MAX distorsion RMSE (%)'], 2), "%")
    print ('')


def _aggregate(d, idxiter):

    print ('Aggrégation des segments de traces candidats')
    print ("    Itération n° :", idxiter)
    print ('    Fin du traitement :', datetime.datetime.fromtimestamp(d['ts']).strftime('%d/%m/%Y %H:%M:%S'))
    print ('')

    print ('Results')
    print ('--------------------------------------------------')
    print ('Number of aggregations :                           ', d['Number of aggregations'])
    print ('Number of aggregations with 30 traces :            ', d['Number of aggregations with 30 traces'])
    print ('Number of aggregations with fewer than 30 traces : ', d['Number of aggregations with fewer than 30 traces'])
    print ('Minimum number of traces in aggregation :          ', d['Minimum number of traces in aggregation'])
    print ('Average number of traces in aggregation :          ', d['Average number of traces in aggregation'])
    print ('')


def _candidate(d, idxiter):

    print ('Préparation des traces pour la fusion: segments candidats')
    print ("    Itération n° :", idxiter)
    print ('    Fin du traitement :', datetime.datetime.fromtimestamp(d['ts']).strftime('%d/%m/%Y %H:%M:%S'))
    print ('')

    print ('Results')
    print ('--------------------------------------------------')
    print ('Number of processed edges :                        ', d['Number of processed edges'])
    print ('Minimum number of candidate traces per edge :      ', d['Minimum number of candidate traces per edge'])
    print ('Maximum number of candidate traces per edge :      ', d['Maximum number of candidate traces per edge'])
    print ('Average number of candidate tracks per edge  :     ', d['Average number of candidate tracks per edge'])
    print ('')


def _env(d):
    print ('Environment information')
    print ('    Fin du traitement :', datetime.datetime.fromtimestamp(d['ts']).strftime('%d/%m/%Y %H:%M:%S'))
    print ('')

    print ('--------------------------------------------------')
    print ('User :                              ', d['User'])
    print ("System :                            ", d['System'])
    print ("Python version :                    ", d['Python version'])
    print ("Heap memory :                       ", d['Heap memory'], " Mo")
    print ('')


def _rawdata(d):
    print ('Informations sur les données en entrée ')
    print ('    Fin du traitement :', datetime.datetime.fromtimestamp(d['ts']).strftime('%d/%m/%Y %H:%M:%S'))
    print ('')

    print ('--------------------------------------------------')
    print ("Number of tracks :                     ", d['Nb traces'])
    print ("Number of traces split :               ", d['Nb traces d\u00e9coup\u00e9es'])
    print ("Number of traces after preprocessing : ", d['Nb traces final'])
    print ('')
    print ("Moyenne des distances :                ", d['Moyenne des distances'], 'm')
    print ("Moyenne du nombre de points :          ", d['Moyenne du nombre de points'])
    print ('')

    print ('Emprise spatiale')
    print ('--------------------------------------------------')
    print (d['Emprise spatiale'])

    print ('')


def _topology(d, idxiter):
    print ('Topologie')
    print ("    Itération n° :", idxiter)
    print ('    Fin du traitement :', datetime.datetime.fromtimestamp(d['ts']).strftime('%d/%m/%Y %H:%M:%S'))
    print ('')

    print ('--------------------------------------------------')
    print ("Number of edges in the skeleton :     ", d['Number of edges in the skeleton'])
    print ("Number of skeleton edges removed for being too short : ", d['Number of skeleton edges removed for being too short'])
    print ('')



def _image(d, idxiter):

    print ('Résultats des calculs matriciels')
    print ("    Itération n° :", idxiter)
    print ('    Fin du traitement :', datetime.datetime.fromtimestamp(d['ts']).strftime('%d/%m/%Y %H:%M:%S'))
    print ('')

    print ("Image Processing Results")
    print ('--------------------------------------------------')
    print ("High-resolution grid cell size :                     ", d['High-resolution grid cell size (m)'], 'm')
    print ("Low-resolution grid cell size :                      ", d['Low-resolution grid cell size (m)'], 'm')
    print ("Number of neighboring cells to consider :            ", d['Number of neighboring cells to consider'])
    print ("Cell cluster size threshold for filling or removal : ", d['Cell cluster size threshold for filling or removal (m2)'], "m2")
    print ('')

    print ("Polygonization Results")
    print ('--------------------------------------------------')
    print ("Number of polygonize features :                     ", d['Number of polygonize features'])
    print ("Number of small polygonized features :              ", d['Number of small polygonized features'])
    print ("Average area of small polygons :                    ", d['Average area of small polygons (m2)'], "m2")
    print ("Number of polygonized features above threshold :    ", d['Number of polygonized features above threshold'])
    print ('')

    print ('--------------------------------------------------')
    print ("Number of edges in the skeleton :     ", d['Number of edges in the skeleton'])
    print ('')



'''
print ('==================================================================================')
print ('#  Qualité')
print ('')
print ('GINI:')
print ('')
'''








