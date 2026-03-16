# -*- coding: utf-8 -*-


from tracklib.core import TrackCollection
from tracklib.algo.interpolation import conflate
from tracklib.algo.comparison import compare, MODE_COMPARISON_POINTWISE



# ---------------------------------------------------------------------------------
# Elastic conflation of segment geometries on a network
# ---------------------------------------------------------------------------------
# Inputs: - geom      : a collection of geometries (TrackCollection)
#         - network   : network containing reference nodes
#         - threshold : distance btw ending points above which conflation aborted
#		  - h         : covariance distance of elastic correction
# Output: a collection of geometries (TrackCollection) preserving the shape of the 
# input geometries while enforcing constraints on ending points defined by network
# Each object in geom must have a tid matching with edge ids of the network
# ---------------------------------------------------------------------------------
# Conflation is performed with 'colocation least squares' method and gaussian 
# covariogram of standard deviation h
# ---------------------------------------------------------------------------------
def conflateOnNetwork(geom, network, threshold=1e300, h=30, verbose=True):
	
	out = TrackCollection()
	if (verbose):
		print("-----------------------------------------------------------------------------------------")
		print("CORRECTION ELASTIQUE DE LA GEOMETRIE DU RESEAU")
		print("-----------------------------------------------------------------------------------------")
	max_total = 0
	rmse_total = 0
	matched = 0
	
	for segment in geom:
		edge = network.getEdge(segment.tid)
		p1 = edge.source.coord
		p2 = edge.target.coord
		
		h11 = p1.distance2DTo(segment[ 0].position); h12 = p2.distance2DTo(segment[-1].position); h1 = (h11**2+h12**2)**0.5/1.414
		h21 = p1.distance2DTo(segment[-1].position); h22 = p2.distance2DTo(segment[ 0].position); h2 = (h21**2+h22**2)**0.5/1.141
		HMIN = min(h1, h2)
	
		if (h2 < h1):
			ptemp = p1; p1 = p2; p2 = ptemp
		
		
		if (HMIN < threshold):
		
			conflated = conflate(segment, [p1, p2], [0, -1], h)
				
			MED = compare(segment, conflated, mode=MODE_COMPARISON_POINTWISE, p=1)
			MSE = compare(segment, conflated, mode=MODE_COMPARISON_POINTWISE, p=2)
			MAX = compare(segment, conflated, mode=MODE_COMPARISON_POINTWISE, p=float('inf'))
			if (verbose):
				print("#{:6s}      MED: {:6.3f} m      RMSE: {:6.3f} m      MAX: {:6.3f} m      MATCH: {:6.3f} m".format(segment.tid, MED, MSE, MAX, HMIN))
			rmse_total += MSE**2
			max_total = max(max_total, MAX)
			matched += 1
			
		else:
			conflated = segment.copy()
			
		conflated.tid = segment.tid	
		out.addTrack(conflated)
	
	if (len(geom) > 2):
		rmse_total = (rmse_total/len(geom)-1)**0.5
		if (verbose):
			print("-----------------------------------------------------------------------------------------")
			print("Number of conflated segments :     ",   matched, "      ({:2.2f}%)".format(matched/len(geom)*100))
			print("Total distorsion RMSE        :  {:6.3f} m     (MAX: {:6.3f} m)".format(rmse_total, max_total))
	if (verbose):
		print("-----------------------------------------------------------------------------------------")
	
	return out
