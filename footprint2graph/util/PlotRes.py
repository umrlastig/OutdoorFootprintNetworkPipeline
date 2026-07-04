# -*- coding: utf-8 -*-


import tracklib as tkl

import csv
import numpy as np
import os
import re

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from mpl_toolkits.axes_grid1 import make_axes_locatable

import fiona
import rasterio
from rasterio.plot import show
from shapely.geometry import LineString, MultiLineString, Polygon
from shapely.geometry import shape as geom_shape




def maPlotRasterTiff(pathres, filename, append):
    with rasterio.open(pathres + filename) as src:
        show(src, ax=append, cmap="Blues")  # Greys


def matPlotShapefile(pathres, filename, append):
    chemin = pathres + filename
    shape = fiona.open(chemin)

    for i in range(len(shape)):
        if (i == 2):
            continue
        feature = shape[i]
        geom = geom_shape(feature["geometry"])

        if isinstance(geom, MultiLineString):
            for line in geom.geoms:
                x, y = line.xy
                append.plot(x, y, 'b-', linewidth=0.5)

        elif isinstance(geom, Polygon):

            # contour extérieur
            x, y = geom.exterior.xy
            append.plot(x, y, 'k-', linewidth=0.5)
            append.fill(x, y, alpha=0.3)

            # trous éventuels
            for interior in geom.interiors:
                x, y = interior.xy
                append.plot(x, y, 'k-', linewidth=0.5)





def plotMM(pathres, squelette = None):

    plt.figure(figsize=(16, 8))

    ax1 = plt.subplot2grid((1, 2), (0, 0))
    ax2 = plt.subplot2grid((1, 2), (0, 1))
    ax1.set_title('Résultat du map-matching')

    if squelette is None:
        fmt = tkl.NetworkFormat({
                   "pos_edge_id": 0,
                   "pos_source": 1,
                   "pos_target": 2,
                   "pos_wkt": 4,
                   "srid": "ENU",
                   "separator": ",",
                   "header": 1})
        networkpath = pathres + 'network/reseau_1.csv'
        squelette = tkl.NetworkReader.readFromFile(networkpath, fmt, verbose=False)

    n = len(squelette.EDGES)
    cmap = plt.cm.get_cmap('tab20', n)
    colors = [cmap(i) for i in range(n)]


    collection = tkl.TrackCollection()
    mmtrackpath = pathres + '/mapmatch/tmm1/'

    XX = {}
    YY = {}

    for mmfilename in os.listdir(mmtrackpath):
        XR = []
        YR = []
        XG = []
        YG = []
        XB = []
        YB = []
        for edge in squelette.EDGES:
            XX[edge] = []
            YY[edge] = []

        #N;E;time;U;num;track_id;user_id;hmm_inference;mmtype;idedge
        fmt = tkl.TrackFormat({'ext': 'CSV',
                                   'srid': 'ENU',
                                   'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                                   'separator': ';',
                                   'header': 0,
                                   'comment': '#',
                                   'read_all': True})
        trace = tkl.TrackReader.readFromFile(mmtrackpath + mmfilename, fmt)
        for j in range(trace.size()):
            obs = trace.getObs(j)
            x = float(obs.position.getX())
            y = float(obs.position.getY())

            s = trace["hmm_inference", j]
            hmminf = list(map(float, re.findall(r"[0-9.]+", s)))
            ds = float(hmminf[4])
            dt = float(hmminf[5])
            edgeid = str(int(trace["idedge", j]))
    
            if str(trace["mmtype", j]) == "NOT":
                # pas de MM
                XR.append(x)
                YR.append(y)
            if str(trace["mmtype", j]) == "EDGE":
                XG.append(hmminf[0])
                YG.append(hmminf[1])

                XX[edgeid].append(x)
                YY[edgeid].append(y)

            if str(trace["mmtype", j]) == "SOURCE" or str(trace["mmtype", j]) == "TARGET":
                XB.append(hmminf[0])
                YB.append(hmminf[1])

        ax1.scatter(XG, YG, color='green', s=3, label='Map-matched on edge')
        ax1.scatter(XR, YR, color='red', s=3, label='Not Map-matched')
        ax1.scatter(XB, YB, color='cyan', s=3, label='Map-matched on node')

        cpt = 0
        for edge in squelette.EDGES:
            color = colors[cpt]
            cpt += 1
            ax2.scatter(XX[edge], YY[edge], color=color, s=3, label='brut')
        ax2.scatter(XR, YR, color='red', s=3, label='Not Map-matched')


    # Supprime les doublons dans la légende
    handles, labels = ax1.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax1.legend(by_label.values(), by_label.keys())


    squelette.plot('k-', nodes='ko', size=0.8, append=ax2)


def plotSegmentsConstruction(pathres, ax, squelette):
    mmpath = pathres + '/mapmatch/resultmm_1.csv'

    n = len(squelette.EDGES)
    cmap = plt.cm.get_cmap('tab20', n)
    colors = [cmap(i) for i in range(n)]

    TRACES = {}
    with open(mmpath, 'r', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in spamreader:
            edgeid   = row[0]
            wkt      = row[3]
            if wkt == 'WKT':
                continue

            if not edgeid in TRACES:
                TRACES[edgeid] = []
            trace = tkl.TrackReader.parseWkt(wkt, 'ENU')
            TRACES[edgeid].append(trace)
    
    for i, edgeid in enumerate(TRACES.keys()):
        color = colors[i]
        for trace in TRACES[edgeid]:
            ax.plot(trace.getX(), trace.getY(), color=color, linestyle='-')
            
    squelette.plot('k-', nodes='ko', size=0.8, append=ax)



def plotAggregation(pathres, ax):
    fusionpath = pathres + '/geometry/fusion1/'
    for fusionfilename in os.listdir(fusionpath):
        with open(fusionpath + fusionfilename, 'r') as file:
            line = file.readline()
            line = file.readline()
            wkt = line.split(";")[2].strip()
            if wkt == 'WKT':
                continue
    
            trace = tkl.TrackReader.parseWkt(wkt, 'ENU')
            ax.plot(trace.getX(), trace.getY(), color='red', linestyle='-')


def plotConflation(pathres, append, size=0.8, label=''):
    raccordpath = pathres + '/geometry/raccord1/'
    for raccordfilename in os.listdir(raccordpath):
        with open(raccordpath + raccordfilename, 'r') as file:
            line = file.readline()
            line = file.readline()
            wkt = line.split(";")[1].strip()
            if wkt == 'WKT':
                continue
    
            trace = tkl.TrackReader.parseWkt(wkt, 'ENU')
            append.plot(trace.getX(), trace.getY(), color='green', linestyle='-',
                    linewidth=size, label=label)

    # Supprime les doublons dans la légende
    handles, labels = append.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    append.legend(by_label.values(), by_label.keys())



def plotSqueletteTopo(pathres, ax):
    output_file = str(pathres) + 'network/squelette_topology_simplifie_1.csv'
    fmt = tkl.NetworkFormat({
           "pos_edge_id": 0,
           "pos_source": 1,
           "pos_target": 2,
           "pos_wkt": 3,
           "srid": "ENU",
           "separator": ",",
           "header": 1})
    network = tkl.NetworkReader.readFromFile(output_file, fmt, verbose=False)
    network.plot('k-', nodes='ko', size=0.8, append=ax)



def plotResultatFinal(pathres, idx):
    fig, ax = plt.subplots(figsize=(20, 16))
    
    fmt = tkl.NetworkFormat({
               "pos_edge_id": 0,
               "pos_source": 1,
               "pos_target": 2,
               "pos_wkt": 4,
               "srid": "ENU",
               "separator": ",",
               "header": 1})
    networkpath = pathres + 'merge_' + str(idx) + '/reseau_mobilite_' + str(idx) + '.csv'
    squelette = tkl.NetworkReader.readFromFile(networkpath, fmt, verbose=False)


    L = list(squelette.EDGES.items())
    for i in range(len(L)):
        x1d = []
        y1d = []
        edge = L[i][1]
        for j in range(edge.geom.size()):
            x1d.append(edge.geom.getX()[j])
            y1d.append(edge.geom.getY()[j])
        ax.plot(x1d, y1d, 'r-', linewidth=3, label='Mobility Network')


    # Supprime les doublons dans la légende
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())


    '''
    #cmap = 'turbo'
    vmin = 0


    # ==========================================================

    chemin = pathres + 'image/G1_1.asc'
    rasterG1 = tkl.RasterReader.readFromAscFile(chemin, name='G1', separator='\t')
    afmap = rasterG1.getAFMap('G1')


    matrice = np.full((afmap.raster.nrow, afmap.raster.ncol),
                      afmap.raster.getNoDataValue(), dtype=np.float32)
    for i in range(afmap.raster.nrow):
        for j in range(afmap.raster.ncol):
            val = float(afmap.grid[i][j])
            if val != afmap.raster.getNoDataValue():
                matrice[i][j] = val
    if afmap.raster.getNoDataValue() != None:
        matrice[matrice == afmap.raster.getNoDataValue()] = np.nan

    if cmap is None:
        cmap = getOffsetColorMap(color1, color2, 0)
        cmap.set_bad(color=novaluecolor)


    extent = [
        afmap.raster.xmin,
        afmap.raster.xmax,
        afmap.raster.ymin,
        afmap.raster.ymax
    ]

    im = plt.imshow(matrice, cmap=cmap, vmin=vmin, extent=extent, origin='upper')
    plt.title(afmap.getName())


    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad=0.1)
    if fig != None:
        fig.colorbar(im, cax=cax, orientation='vertical', fraction=0.046)
    '''

