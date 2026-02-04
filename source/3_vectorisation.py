# -*- coding: utf-8 -*-


from util import plotRaster

'''
    
    Travail sur l'image
    - Filtre morphologique : dilatation puis erosion 
    - Squeletisation
    - Vectorisation
    - center line dans Postgis

    A lancer dans la console QGIS + connection à Postgis

'''


# On supprime toutes les couches du projet
QgsProject.instance().removeAllMapLayers()


ascpath = r'/home/md_vandamme/4_RESEAU/V2/zone1/zone1_B_V1.asc'


# =============================================================================

def plotRaster(pathres, title):

    layerGrid = QgsRasterLayer(pathres, title, "gdal")
    layerGrid.setCrs(QgsCoordinateReferenceSystem("EPSG:2154"))
    QgsProject.instance().addMapLayer(layerGrid)

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
    layerGrid.triggerRepaint()


# =============================================================================
#  On charge le binaire


rasterB = tkl.RasterReader.readFromAscFile(ascpath, name='B', separator='\t')
grille = rasterB.getAFMap('B')

plotRaster(ascpath, "G1")


# =============================================================================
#  Ouverture



