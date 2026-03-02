# -*- coding: utf-8 -*-


import tracklib as tkl

tracepath  = r'/home/md_vandamme/5_GPS/OV/BAUGES/walk/6736477209049897211.csv'
fmt = tkl.TrackFormat({'ext': 'CSV',
                       'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': -1,
                       'srid': 'ENUCoords',
                       'separator': ';',
                       'header': 0,
                       'cmt': '#',
                       'read_all': True,
                       #'aftypes': [('num', str)]
                       'verbose': False})

trace = tkl.TrackReader.readFromFile(tracepath, fmt)
print ("Size of track ", trace.size())

num = trace.getObsAnalyticalFeature('num', 0)
print (num, type(num))

idxSelect = 10
version = "v" + str(idxSelect)
trace.createAnalyticalFeature('version', version, str)



af_names = ['num', 'version']
tracespath = "/home/md_vandamme/0_T/aa.csv"
tkl.TrackWriter.writeToFile(trace, tracespath,
                             id_E=1, id_N=0, id_U=3, id_T=2,
                             h=1, separator=";", af_names=af_names)


#version = trace.getObsAnalyticalFeature('version', 0)
#print (version, type(version))