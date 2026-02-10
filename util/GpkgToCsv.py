# -*- coding: utf-8 -*-

'''

    Script préparatoire qui lit un géopackage d'outdoorvision et
    qui construit un fichier CSV par trace.

    Gère de 1 à n packages en même temps.
    Gère 4 activités : walk, run, vélo, ski

    Les attributs sont mis comme AF.

    Les traces sont projetées en Lambert93

'''


import fiona
import matplotlib.pyplot as plt
import tracklib as tkl

# set format for timestamp
tkl.ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")

# 5062
# 'running', 'walking', 'cycling', 'skiing'

chemin = '/home/md_vandamme/5_DATA/OV/'

FICS = ['Export_Chamonix_0.gpkg', 'Export_Chamonix_1.gpkg', 'Export_Les_Houches_0.gpkg',
        'Export_Servoz_0.gpkg', 'Export_Vallorcine_0.gpkg']

NOMS = ['Export_Chamonix_0', 'Export_Chamonix_1', 'Export_Les_Houches_0',
        'Export_Servoz_0', 'Export_CCVCMB_0']

csvpath1 = '/home/md_vandamme/5_DATA/OV/CHAM/walk/'
csvpath2 = '/home/md_vandamme/5_DATA/OV/CHAM/run/'
csvpath3 = '/home/md_vandamme/5_DATA/OV/CHAM/velo/'
csvpath4 = '/home/md_vandamme/5_DATA/OV/CHAM/ski/'


cpt = 1
for i, fic in enumerate(FICS):
    pat = chemin + fic
    with fiona.open(pat, layer=NOMS[i]) as layer:
        for feature in layer:
            geom = feature['geometry']
            if geom.type == 'LineString':
                prop = feature.properties
    
                track_id = prop['track_id']
                user_id = prop['user_id']
                trace = tkl.Track(track_id=track_id)
    
                ide = int(prop['id'])
                date_start = str(prop['date_start'])
                if len(date_start) > 19:
                    date_start = date_start[0:19]
                date_end = prop['date_end']
    
                coords = feature.geometry["coordinates"]
                for c in coords:
                    time = tkl.ObsTime()
                    point = tkl.Obs(tkl.GeoCoords(c[0], c[1], 0), time)
                    trace.addObs(point)
    
                trace.createAnalyticalFeature('num', int(ide))
                trace.createAnalyticalFeature('track_id', int(track_id))
                trace.createAnalyticalFeature('user_id', int(user_id))
                trace.createAnalyticalFeature('date_start', date_start)
                trace.createAnalyticalFeature('date_end', str(date_end))
    
                af_names = ['num', 'track_id', 'user_id', 'date_start', 'date_end']
    
                # Changement du système de référence: on projete en Lambert93
                trace.toProjCoords(2154)
    
                activity = prop['activity']
    
                if activity == 'walking':
                    # on ajoute la trace
                    path = csvpath1 + str(track_id) + ".csv"
                    tkl.TrackWriter.writeToFile(trace, path,
                                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                                 h=1, separator=";", af_names=af_names)
    
                if activity == 'running':
                    # on ajoute la trace
                    path = csvpath2 + str(track_id) + ".csv"
                    tkl.TrackWriter.writeToFile(trace, path,
                                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                                 h=1, separator=";", af_names=af_names)
    
                if activity == 'cycling':
                    # on ajoute la trace
                    path = csvpath3 + str(track_id) + ".csv"
                    tkl.TrackWriter.writeToFile(trace, path,
                                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                                 h=1, separator=";", af_names=af_names)
                if activity == 'skiing':
                    # on ajoute la trace
                    path = csvpath4 + str(track_id) + ".csv"
                    tkl.TrackWriter.writeToFile(trace, path,
                                                 id_E=1, id_N=0, id_U=3, id_T=2,
                                                 h=1, separator=";", af_names=af_names)
    
    
                cpt += 1
                if cpt%1000 == 0:
                    print (cpt)













