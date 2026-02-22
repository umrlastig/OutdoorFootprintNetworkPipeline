# -*- coding: utf-8 -*-

from osgeo import gdal, ogr, osr


RESPATH = r'/home/md_vandamme/4_RESEAU/Ex2Z1Walk/' + 'image/'
pathdilatation  = RESPATH + 'dilatation.tif'
roadsurfpath = RESPATH + 'road_surface.shp'


#  get raster datasource
src_ds = gdal.Open(pathdilatation)
srcband = src_ds.GetRasterBand(1)

dst_layername = 'road_surface'
drv = ogr.GetDriverByName("ESRI Shapefile")
dst_ds = drv.CreateDataSource(roadsurfpath)
sp_ref = osr.SpatialReference()
sp_ref.SetFromUserInput('EPSG:2154')

dst_layer = dst_ds.CreateLayer(dst_layername, srs=sp_ref)

fld = ogr.FieldDefn("DN", ogr.OFTInteger)
dst_layer.CreateField(fld)
dst_field = dst_layer.GetLayerDefn().GetFieldIndex("DN")

gdal.Polygonize(srcband, None, dst_layer, dst_field, [], callback=None )

del src_ds
del dst_ds