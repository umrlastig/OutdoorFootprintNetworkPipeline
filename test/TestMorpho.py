import math
import matplotlib.pyplot as plt
import os
import sys

import numpy as np

module_path = os.path.abspath(os.path.join("/home/YMeneroux/Documents/2-Tracklib/tracklib"))
if module_path not in sys.path:
    sys.path.append(module_path)
    
import tracklib as trk


# ----------------------------------------------------------------------
# Génération de traces synthétiques
# ----------------------------------------------------------------------

trk.stochastics.seed(12345)

def vx(x,y):
    return (y/10)**3
def vy(x,y):
    return (x**2-x-2)/10.0

TRACKS = trk.TrackCollection(trk.generateDataSet(vx, vy, 1000, (-5,-10), (5,10), Nbmax=1000))

for i in range(len(TRACKS)):
    track = TRACKS[i]
    track["count"] = 1
    #plt.plot(track.getX(), track.getY(), 'k-', linewidth=0.5)

# ----------------------------------------------------------------------
# Création d'une carte de chaleur
# ----------------------------------------------------------------------

raster = trk.summarize(TRACKS, ["count"], [trk.co_sum], resolution=(0.1, 0.1), margin=0)
mapCount = raster.getAFMap('count#co_sum')

mapCount.grid = mapCount.grid - (mapCount.grid == trk.NO_DATA_VALUE)*trk.NO_DATA_VALUE




# ----------------------------------------------------------------------
# Ouverture
# ----------------------------------------------------------------------

mask = np.array([
	[0,0,1,0,0], 
	[0,1,1,1,0],
	[1,1,1,1,1],
	[0,1,1,1,0],
	[0,0,1,0,0]])
	
 # Conversion en carte binaire
mapCount.filter(np.array([[1]]), lambda x : 1*(x>1))     


# Erosion
mapCount.filter(np.array([[1]]), lambda x : 1-x)     # Dual de la carte
mapCount.filter(mask, np.max)                        # Dilatation
mapCount.filter(np.array([[1]]), lambda x : 1-x)     # Dual de la carte

# Dilatation
mapCount.filter(mask, np.max)                      
# ----------------------------------------------------------------------


mapCount.plotAsImage()
plt.show()








