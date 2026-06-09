# -*- coding: utf-8 -*-

import sys

try:
    import fiona
except ImportError:
    print ('Code running in a no fiona environment')

import datetime
import progressbar
import numpy as np

from rtree import index
from scipy.spatial import Voronoi

try:
    import shapely
    from shapely.ops import unary_union
    from shapely.geometry import mapping, shape
    from shapely.geometry import LineString, Point, MultiLineString
    from shapely.geometry import MultiPolygon
except ImportError:
    print ('Code running in a no shapely environment')

import matplotlib.pyplot as plt




class Centerline(object):
    '''
    CLASS FOR COMPUTING CENTER LINES
    '''

    def __init__(self, inputGEOM, dist, clean_dist):
        self.inputGEOM = inputGEOM
        self.dist = abs(dist)
        self.clean_dist = clean_dist

    def createCenterline(self, verbose=True):
        """
        Calculates the centerline of a polygon.

        Densifies the border of a polygon which is then represented by a Numpy
        array of points necessary for creating the Voronoi diagram. Once the
        diagram is created, the ridges located within the polygon are
        joined and returned.

        Returns:
            a union of lines that are located within the polygon.
        """

        minx = int(min(self.inputGEOM.envelope.exterior.xy[0]))
        miny = int(min(self.inputGEOM.envelope.exterior.xy[1]))

        if verbose:
            print("\r\n*["+str(datetime.datetime.now())+"]  Upsampling polygon borders...")
        border = np.array(self.densifyBorder(self.inputGEOM, minx, miny))

        vor = Voronoi(border)
        vertex = vor.vertices

        if verbose:
            print("\r\n*["+str(datetime.datetime.now())+"]  Computing polygon skeleton...")
        lst_lines = []
        Nvor = len(list(vor.ridge_vertices))
        if verbose:
            bar = progressbar.ProgressBar(max_value = Nvor)
        for j, ridge in enumerate(vor.ridge_vertices):
            if verbose:
                bar.update(j)
            if -1 not in ridge:
                line = LineString([
                    (vertex[ridge[0]][0] + minx, vertex[ridge[0]][1] + miny),
                    (vertex[ridge[1]][0] + minx, vertex[ridge[1]][1] + miny)])
                if len(line.coords[0]) > 1:
                    lst_lines.append(line)
        if verbose:
            bar.finish()


        input_geom_buffer = shapely.buffer(self.inputGEOM, self.clean_dist)

        if verbose:
            print("\r\n*["+str(datetime.datetime.now())+"]  Filtering skeleton to form center line...")            
        lst_lines_out = []
        if verbose:
            bar = progressbar.ProgressBar(max_value = len(lst_lines))
        for i in range(len(lst_lines)):
            if verbose:
                bar.update(i)
            if not (shapely.contains(input_geom_buffer, lst_lines[i])):
                continue            
            lst_lines_out.append(lst_lines[i])
        if verbose:
            bar.finish()

        return unary_union(lst_lines_out)
        

    def densifyBorder(self, polygon, minx, miny):
        """
        Densifies the border of a polygon by a given factor (by default: 5).

        The function tests the complexity of the polygons geometry, i.e. does
        the polygon have holes or not. If the polygon doesn't have any holes,
        its exterior is extracted and densified by a given factor. If the
        polygon has holes, the boundary of each hole as well as its exterior is
        extracted and densified by a given factor.

        Returns:
            a list of points where each point is represented by a list of its
            reduced coordinates.

        Example:
            [[X1, Y1], [X2, Y2], ..., [Xn, Yn]
        """
        if isinstance(polygon, MultiPolygon):
            # print("C'est un MultiPolygon !!!!!!")

            cpt = 0
            for poly in polygon.geoms:
                if len(poly.interiors) == 0:
                    exterIN = LineString(poly.exterior)
                    if cpt == 0:
                        points = self.fixedInterpolation(exterIN, minx, miny, verbose=True)
                    else:
                        points += self.fixedInterpolation(exterIN, minx, miny, verbose=True)
                else:
                    exterIN = LineString(poly.exterior)
                    if cpt == 0:
                        points = self.fixedInterpolation(exterIN, minx, miny, verbose=True)
                    else:
                        points += self.fixedInterpolation(exterIN, minx, miny, verbose=True)
                    for j in range(len(poly.interiors)):
                        interIN = LineString(poly.interiors[j])
                        points += self.fixedInterpolation(interIN, minx, miny)
                cpt +=1

        else:
            # print("C'est un Polygon !!!!!!")

            if len(polygon.interiors) == 0:
                exterIN = LineString(polygon.exterior)
                points = self.fixedInterpolation(exterIN, minx, miny, verbose=True)
    
            else:
                exterIN = LineString(polygon.exterior)
                points = self.fixedInterpolation(exterIN, minx, miny, verbose=True)
    
                for j in range(len(polygon.interiors)):
                    interIN = LineString(polygon.interiors[j])
                    points += self.fixedInterpolation(interIN, minx, miny)

        return points

    def fixedInterpolation(self, line, minx, miny, verbose=False):
        """
        A helping function which is used in densifying the border of a polygon.

        It places points on the border at the specified distance. By default the
        distance is 5 (meters) which means that the first point will be placed
        5 m from the starting point, the second point will be placed at the
        distance of 1.0 m from the first point, etc. Naturally, the loop breaks
        when the summarized distance exceeds the length of the line.

        Returns:
            a list of points where each point is represented by a list of its
            reduced coordinates.

        Example:
            [[X1, Y1], [X2, Y2], ..., [Xn, Yn]
        """

        count = self.dist
        newline = []

        startpoint = [line.xy[0][0] - minx, line.xy[1][0] - miny]
        endpoint = [line.xy[0][-1] - minx, line.xy[1][-1] - miny]
        newline.append(startpoint)

        if (verbose):
            bar = progressbar.ProgressBar(max_value=int(line.length)+1)

        while count < line.length:
            point = line.interpolate(count)
            newline.append([point.x - minx, point.y - miny])
            if (verbose):
                bar.update(int(count))
            count += self.dist
        newline.append(endpoint)
       
        if (verbose):
            bar.finish()

        return newline



class Shp2centerline(object):
    '''
    MAIN CLASS FOR EXECUTING CENTER LINE COMPUTATION ON A SHAPE FILE
    '''

    def __init__(self, inputSHP, outputSHP, dist, clean_dist, verbose=True):
        self.inshp = inputSHP
        self.outshp = outputSHP

        self.dist = abs(dist)
        self.clean_dist = clean_dist

        self.verbose = verbose

        self.dct_polygons = {}
        self.dct_centerlines = {}

        # ------------------------------------------------------------------------
        # Load polygon from input file
        # ------------------------------------------------------------------------
        if self.verbose:
            print('*['+str(datetime.datetime.now())+']  Importing polygons from: [' + self.inshp + ']... ', end='')
        self.importSHP()
        if self.verbose:
            print("done\r\n")
        
        # ------------------------------------------------------------------------
        # Computing center line
        # ------------------------------------------------------------------------
        if self.verbose:
            print('*['+str(datetime.datetime.now())+']  Center line computation')
        self.run()
        
        # ------------------------------------------------------------------------
        # Output center line
        # ------------------------------------------------------------------------
        if self.verbose:
            print('\r\n*['+str(datetime.datetime.now())+']  Exporting center line to: [' + self.outshp+ ']... ', end='')
        self.export2SHP()
        if self.verbose:
            print("done")

    def run(self):
        """
        Starts processing the imported SHP file.
        It sedns the polygon's geometry allong with the interpolation distance
        to the Centerline class to create a Centerline object.
        The results (the polygon's ID and the geometry of the centerline) are
        added to the dictionary.
        """

        for key in self.dct_polygons.keys():
            poly_geom = self.dct_polygons[key]
            centerlineObj = Centerline(poly_geom, self.dist, self.clean_dist)

            self.dct_centerlines[key] = centerlineObj.createCenterline(self.verbose)

    def importSHP(self):
        """
        Imports the Shapefile into a dictionary. Shapefile needs to have an ID
        column with unique values.

        Returns:
            a dictionary where the ID is the key, and the value is a polygon
            geometry.
        """

        with fiona.open(self.inshp, 'r', encoding='UTF-8') as fileIN:
            for polygon in fileIN:
                polygonID = polygon['properties'][u'id']
                geom = shape(polygon['geometry'])

                self.dct_polygons[polygonID] = geom

    def export2SHP(self):
        """
        Creates a Shapefile and fills it with centerlines and their IDs.

        The dictionary contains the IDs of the centerlines (keys) and their
        geometries (values). The ID of a centerline is the same as the ID of
        the polygon it represents.
        """

        newschema = {'geometry': 'MultiLineString',
                     'id': 'int',
                     'properties': {'id': 'int'}}

        with fiona.open(self.outshp, 'w', encoding='UTF-8',
                        schema=newschema, driver='ESRI Shapefile') as SHPfile:

            for i, key in enumerate(self.dct_centerlines):
                geom = self.dct_centerlines[key]
                if geom.length <= 0.0:
                    continue

                if geom.geom_type == 'LineString':
                    geom = MultiLineString([geom])
                #print(shapely.is_valid(geom))
                #print (geom.length)
                #print (geom.geom_type)
                #print (shapely.to_wkt(geom))

                newline = {}
                newline['id'] = key
                newline['geometry'] = mapping(geom)
                newline['properties'] = {'id': key}

                SHPfile.write(newline)


