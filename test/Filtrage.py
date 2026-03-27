import os
import sys
import math
import fiona
import random
import numpy as np
import matplotlib.pyplot as plt

from shapely.geometry import shape as geom_shape



import tracklib as trk


# ------------------------------------------------------------------
# Paramètres
# ------------------------------------------------------------------
r = 2   # Raster resolution
f = 2   # Cut factor
# ------------------------------------------------------------------

# --------------------------------------------------------------------------------------
# Filtre de Fourier coupe-bande sur une géométrie
# --------------------------------------------------------------------------------------
# Inputs:
#    - geom  : polygone (simple)
#    - r     : résolution centrale de coupure (en m)
#    - f     : facteur de coupure
# Output: géométrie filtrée avec suppression de toutes les longueurs d'onde comprises 
# entre r/f et r*f
# --------------------------------------------------------------------------------------
def smoothing(geom, r, f):

	# Préparation
    wl_sup = r*f
    wl_inf = r/f
	
    x = [p[0] for p in geom]
    y = [p[1] for p in geom]
	
    trace = trk.Track()
    for ii in range(len(x)):
        trace.addObs(trk.Obs(trk.ENUCoords(x[ii], y[ii], 0)))

    N = len(trace)
    
    # Centrage du signal
    trace = trace.copy()
    c0 = trace.getCentroid(); 
    cx = c0.E; cy = c0.N
    trace.translate(-cx, -cy)
    
    # Sauvegarde des extrémités
    ci = trace[0]
    cf = trace[-1]
    
    # Periodisation du signal
    geom_in = trace + trace + trace
    
    # Filtre coupe-bande
    signal_low_freq = trk.filter_freq(geom_in, (1.0/wl_sup), mode=trk.FILTER_SPATIAL, type=trk.FILTER_LOW_PASS , dim=trk.FILTER_XY)[N:2*N]
    signal_hgh_freq = trk.filter_freq(geom_in, (1.0/wl_inf), mode=trk.FILTER_SPATIAL, type=trk.FILTER_HIGH_PASS, dim=trk.FILTER_XY)[N:2*N]
   
    # Somme passe-haut/passe-bas
    out = trace.copy()
    for i in range(N):
        out[i, "x"] = signal_low_freq[i, "x"] + signal_hgh_freq[i, "x"]
        out[i, "y"] = signal_low_freq[i, "y"] + signal_hgh_freq[i, "y"] 
        
    # Reconstruction des extrémités 
    out[0]  = ci
    out[-1] = cf   
        
    # Decentrage du signal
    out.translate(cx, cy)
    
    # Retransformation en géométrie
    out_geom = [(obs.position.getX(), obs.position.getY()) for obs in out]
    
    return out_geom





shape = fiona.open("/home/md_vandamme/4_RESEAU/Ex2Z1Walk/image/road_surface_PT.shp")


for i in range(len(shape)):
	if (i == 2):
		continue
	feature = shape[i]
	geom = geom_shape(feature["geometry"])
	exterior = list(geom.exterior.coords)
	interior = [list(r.coords) for r in geom.interiors]
	
	#print("EXTERIOR", i)
		
	x = [p[0] for p in exterior]
	y = [p[1] for p in exterior]
	plt.plot(x, y, 'b-', linewidth=0.5)
	
	# ------------------------------------------------------------------
	# Géométrie filtrée
	# ------------------------------------------------------------------
	out = smoothing(exterior, r, f)
	xout = [p[0] for p in out]
	yout = [p[1] for p in out]
	plt.plot(xout, yout, 'r-', linewidth=0.75)


	# ==================================================================
	# Gestion des intérieurs éventuels
	# ==================================================================
	for j in range(len(interior)):
		#print("  INTERIOR", i, j)
		x = [p[0] for p in interior[j]]
		y = [p[1] for p in interior[j]]
		plt.plot(x, y, 'b-', linewidth=0.5)
		
		# ------------------------------------------------------------------
		# Géométrie filtrée
		# ------------------------------------------------------------------
		out = smoothing(interior[j], r, f)
		xout = [p[0] for p in out]
		yout = [p[1] for p in out]
		plt.plot(xout, yout, 'r-', linewidth=0.75)


plt.show()
