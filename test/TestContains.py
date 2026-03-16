# -*- coding: utf-8 -*-

import shapely
#from shapely.ops import unary_union
#from shapely.geometry import mapping, shape
from shapely.geometry import LineString, Polygon
from shapely.plotting import plot_polygon, plot_line



coords = ((0.0, 0.0), (6.0, 0.0), (6.0, 6.0), (3.0, 6.0), (3.0, 3.0), (0.0, 3.0), (0.0, 0.0))
P = Polygon(coords)
plot_polygon(P)

coords = ((1.5, 1.5), (4.5, 4.5))
L = LineString(coords)
plot_line(L)

if shapely.contains(P, L):
    print ('contains')
else:
    print ('not contains')
