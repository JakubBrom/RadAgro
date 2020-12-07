"""
Zonal Statistics
Vector-Raster Analysis
Copyright 2013 Matthew Perry
Changes: 2019 Jakub Brom
Usage:
  zonal_stats.py VECTOR RASTER METHOD
  zonal_stats.py -h | --help
  zonal_stats.py --version
Options:
  -h --help     Show this screen.
  --version     Show version.
"""
from osgeo import gdal, ogr, osr
from osgeo.gdalconst import *
from scipy import stats
import numpy as np
import sys
from matplotlib import pyplot as plt
gdal.PushErrorHandler('CPLQuietErrorHandler')


def bbox_to_pixel_offsets(gt, bbox):
	originX = gt[0]
	originY = gt[3]
	pixel_width = gt[1]
	pixel_height = gt[5]
	x1 = int((bbox[0] - originX) / pixel_width)
	x2 = int((bbox[1] - originX) / pixel_width) + 1

	y1 = int((bbox[3] - originY) / pixel_height)
	y2 = int((bbox[2] - originY) / pixel_height) + 1

	xsize = x2 - x1
	ysize = y2 - y1
	return (x1, y1, xsize, ysize)


def zonal_stats(vector_path, raster_path, method = 'median', nodata_value=None, global_src_extent=False):
	rds = gdal.Open(raster_path, GA_ReadOnly)
	assert(rds)
	rb = rds.GetRasterBand(1)
	rgt = rds.GetGeoTransform()

	if nodata_value:
		nodata_value = float(nodata_value)
		rb.SetNoDataValue(nodata_value)

	vds = ogr.Open(vector_path, GA_ReadOnly)  # TODO maybe open update if we want to write stats
	assert(vds)
	vlyr = vds.GetLayer(0)

	# create an in-memory numpy array of the source raster data
	# covering the whole extent of the vector layer
	# Reproject vector geometry to same projection as raster
	if global_src_extent:
		# use global source extent
		# useful only when disk IO or raster scanning inefficiencies are your limiting factor
		# advantage: reads raster data in one pass
		# disadvantage: large vector extents may have big memory requirements
		src_offset = bbox_to_pixel_offsets(rgt, vlyr.GetExtent())
		src_array = rb.ReadAsArray(*src_offset)

		# calculate new geotransform of the layer subset
		new_gt = (
			(rgt[0] + (src_offset[0] * rgt[1])),
			rgt[1],
			0.0,
			(rgt[3] + (src_offset[1] * rgt[5])),
			0.0,
			rgt[5]
		)

	mem_drv = ogr.GetDriverByName('Memory')
	driver = gdal.GetDriverByName('MEM')

	# Loop through vectors
	statists = []
	feat = vlyr.GetNextFeature()
	while feat is not None:

		if not global_src_extent:
			# use local source extent
			# fastest option when you have fast disks and well indexed raster (ie tiled Geotiff)
			# advantage: each feature uses the smallest raster chunk
			# disadvantage: lots of reads on the source raster
			src_offset = bbox_to_pixel_offsets(rgt, feat.geometry().GetEnvelope())
			try:
				src_array = rb.ReadAsArray(*src_offset).astype(np.float32)
			except:
				src_array = None

			# calculate new geotransform of the feature subset
			new_gt = (
				(rgt[0] + (src_offset[0] * rgt[1])),
				rgt[1],
				0.0,
				(rgt[3] + (src_offset[1] * rgt[5])),
				0.0,
				rgt[5]
			)

		# Create a temporary vector layer in memory
		mem_ds = mem_drv.CreateDataSource('out')
		mem_layer = mem_ds.CreateLayer('poly', None, ogr.wkbPolygon)
		mem_layer.CreateFeature(feat.Clone())

		# Rasterize it
		rvds = driver.Create('', src_offset[2], src_offset[3], 1, gdal.GDT_Byte)
		rvds.SetGeoTransform(new_gt)
		gdal.RasterizeLayer(rvds, [1], mem_layer, burn_values=[1])
		rv_array = rvds.ReadAsArray()

		# Mask the source data array with our current feature
		# we take the logical_not to flip 0<->1 to get the correct mask effect
		# we also mask out nodata values explictly
		# masked = np.ma.MaskedArray(
			# src_array,
			# mask=np.logical_or(
				# src_array == nodata_value,
				# np.logical_not(rv_array)
			# )
		# )

		# mask data by feature - nans are omitted in calculation
		rv_array = np.where(rv_array == 0, np.nan, rv_array)
		# print(rv_array)
		# print(src_array)
		if src_array is None:
			masked = np.where(rv_array == 1, np.nan, np.nan)
		else:
			masked = src_array * rv_array

		# calculation statistics:
		if method == 'median':
			feature_stats = {'fid': int(feat.GetFID()), 'median': float(np.nanmedian(masked))}
		elif method == 'min':
			feature_stats = {'fid': int(feat.GetFID()),'min': float(np.nanmin(masked))}
		elif method == 'max':
			feature_stats = {'fid': int(feat.GetFID()),'max': float(np.nanmax(masked))}
		elif method == 'std':
			feature_stats = {'fid': int(feat.GetFID()),'std': float(np.nanstd(masked))}
		elif method == 'sum':
			feature_stats = {'fid': int(feat.GetFID()),'sum': float(np.nansum(masked))}
		elif method == 'count':
			feature_stats = {'fid': int(feat.GetFID()),'count': float(np.count_nonzero(~np.isnan(masked)))}
		elif method == 'mean':
			feature_stats = {'fid': int(feat.GetFID()),'mean': float(np.nanmean(masked))}
		elif method == 'mode':
			masked_flat = masked.flatten()
			feature_stats = {'fid': int(feat.GetFID()),'mode':
				int(np.nan_to_num(stats.mode(masked_flat)[0]))}

		statists.append(feature_stats)

		rvds = None
		mem_ds = None
		feat = vlyr.GetNextFeature()

	vds = None
	rds = None
	return statists

