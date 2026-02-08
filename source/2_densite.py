# -*- coding: utf-8 -*-

'''
    Calculs des cartes de densités, de constraste et binaire
    A lancer dans la console QGIS

'''

import sys
import csv
csv.field_size_limit(sys.maxsize)

import tracklib as tkl

from tracklib.util.qgis import QGIS, LineStyle, PointStyle


# =============================================================================

G1_SIZE = 2
G2_SIZE = 50
SEUIL = 15

resampledtracespath = r'/home/md_vandamme/4_RESEAU/ExampleTest/resample/'
respath             = r'/home/md_vandamme/4_RESEAU/ExampleTest/densite/'


# =============================================================================


def styleTurbo(layerGrid):
    style = QgsStyle().defaultStyle()
    ramp = style.colorRamp("Turbo")

    color_ramp = QgsColorRampShader()
    color_ramp.setColorRampType(QgsColorRampShader.Interpolated)

    provider = layerGrid.dataProvider()
    stats = provider.bandStatistics(1)
    vmin, vmax = 0, stats.maximumValue

    nb_classes = 256
    items = []
    for i in range(nb_classes):
        value = float(vmin) + (vmax - vmin) * float(i) / (nb_classes - 1)
        color = ramp.color(i / (nb_classes - 1))
        items.append(QgsColorRampShader.ColorRampItem(value, color))
    color_ramp.setColorRampItemList(items)

    shader = QgsRasterShader()
    shader.setRasterShaderFunction(color_ramp)

    renderer = QgsSingleBandPseudoColorRenderer(provider, 1, shader)
    renderer.setClassificationMin(0)
    renderer.setClassificationMax(stats.maximumValue)

    layerGrid.setRenderer(renderer)


def plotRaster(pathres, title, style=None):

    layerGrid = QgsRasterLayer(pathres, title, "gdal")
    layerGrid.setCrs(QgsCoordinateReferenceSystem("EPSG:2154"))
    QgsProject.instance().addMapLayer(layerGrid)

    if style is not None and style == 'Turbo':
        styleTurbo(layerGrid)
        layerGrid.triggerRepaint()



# =============================================================================
#       Chargement des traces GPS
#  Ici elles sont mises dans un fichier CSV dont la géométrie de la trace est
#  dans le format WKT

fmt = tkl.TrackFormat({'ext': 'CSV',
                       'srid': 'ENU',
                       'id_E': 1,'id_N': 0, 'id_U': 3,'id_T': 2,
                       'separator': ';',
                       'header': 1})

cptId = 1
collection = tkl.TrackReader.readFromFile(resampledtracespath, fmt)
for trace in collection:
    trace.uid = cptId
    trace.tid = cptId
    cptId += 1
print ('Number of tracks : ', collection.size())



QGIS.plotTracks(collection, type='POINT',
                style=PointStyle.circleYellow,
                title='Zone3-walk points')
QGIS.plotTracks(collection, type='LINE',
                style=LineStyle.simpleLightOrange,
                title='Zone3-walk line')



# =============================================================================
#       Calcul des densités des traces GPS


af_algos = ['uid']
cell_operators = [tkl.co_count_distinct]

marge = 0
resolutionG1 = (G1_SIZE, G1_SIZE)
bbox = collection.bbox()

rasterG1 = tkl.summarize(collection, af_algos, cell_operators, resolutionG1, marge,
                   align=tkl.BBOX_ALIGN_CENTER)
grilleG1 = rasterG1.getAFMap('uid#co_count_distinct')
for i in range(grilleG1.raster.nrow):
    for j in range(grilleG1.raster.ncol):
        grilleG1.grid[i][j] = grilleG1.grid[i][j] / (G1_SIZE*G1_SIZE)

pathG1 = respath + 'G1.asc'
tkl.RasterWriter.writeMapToAscFile(pathG1, grilleG1)

plotRaster(pathG1, "G1", "Turbo")

# Combien de cellules de chaque côté pour la petite résolution ?
nb = math.floor(G2_SIZE / G1_SIZE)



# =============================================================================

epsilon = 0.001
# On construit une grille vide comme G1
box = tkl.Bbox(tkl.ENUCoords(rasterG1.xmin, rasterG1.ymin),
               tkl.ENUCoords(rasterG1.xmax, rasterG1.ymax))
res = rasterG1.resolution
margin = 0
align = tkl.BBOX_ALIGN_CENTER
rasterK = tkl.Raster(bbox=box, resolution=res, margin=margin, align=align)
rasterK.addAFMap('K')

from scipy.ndimage import maximum_filter
G2 = maximum_filter(grilleG1.grid, size=nb)

for i in range(rasterK.nrow):
    for j in range(rasterK.ncol):
        x = rasterK.xmin + j * res[0] + 1
        y = rasterK.ymin - (i - rasterK.nrow + 1) * res[1] + 1
        (column, line) = rasterG1.getCell(tkl.ENUCoords(x, y))
        g1 = grilleG1.grid[line][column]

        g2 = G2[line][column] / (nb * G1_SIZE * nb * G1_SIZE)

        if g1 <= 2:
            g1 = 0

        if g2 <= 0:
            g2 = epsilon

        k = g1 / g2

        rasterK.getAFMap(0).grid[i][j] = k

grilleK = rasterK.getAFMap(0)

pathK = respath + 'K.asc'
tkl.RasterWriter.writeMapToAscFile(pathK, grilleK)

plotRaster(pathK, "K", "Turbo")



# =============================================================================

# On construit une grille vide comme G1
box = tkl.Bbox(tkl.ENUCoords(rasterK.xmin, rasterK.ymin),
               tkl.ENUCoords(rasterK.xmax, rasterK.ymax))
res = rasterK.resolution
margin = 0
align = tkl.BBOX_ALIGN_CENTER
raster = tkl.Raster(bbox=box, resolution=res, margin=margin, align=align)
raster.addAFMap('B')

for i in range(raster.nrow):
    for j in range(raster.ncol):
        v = grilleK.grid[i][j]
        if v > SEUIL:
            raster.getAFMap(0).grid[i][j] = 1
        else:
            raster.getAFMap(0).grid[i][j] = 0

pathB = respath + 'B.asc'
tkl.RasterWriter.writeMapToAscFile(pathB, raster.getAFMap(0))

plotRaster(pathB, "B")


# =============================================================================


print ("Fin des calculs des cartes de densités, de constraste et binaire.")


print ("END SCRIPT 2.")




