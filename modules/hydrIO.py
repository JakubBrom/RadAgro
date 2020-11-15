#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------
# RadHydro 
#
# Module: hydrIO.py
#
# Author: Jakub Brom, University of South Bohemia in Ceske Budejovice,
#		  Faculty of Agriculture 
#
# Date: 2018/11/08
#
# Description:
# 
# License: Copyright (C) 2018-2020, Jakub Brom, University of South Bohemia
#		   in Ceske Budejovice
# 
# Vlastníkem programu RadHydro je Jihočeská univerzita v Českých 
# Budějovicích. Všechna práva vyhrazena. Licenční podmínky jsou uvedeny
# v licenčním ujednání (dále jen "smlouva").
# Uživatel instalací nebo použitím programu, jeho verzí nebo aktualizací
# souhlasí s podmínkami smlouvy.
# -----------------------------------------------------------------------

# imports
import numpy as np
import os

from osgeo import gdal, osr, ogr


def rasterToArray(layer):
	"""Conversion of raster layer to numpy array.
	:param layer: Path to raster layer.
	:type layer: str
	
	:return: raster file converted to numpy array
	"""

	try:
		if layer is not None:
			in_layer = gdal.Dataset.ReadAsArray(gdal.Open(layer)).astype(
				np.float32)
		else:
			in_layer = None
		return in_layer
	except FileNotFoundError:
		in_layer = None
		return in_layer

def readGeo(rast):
	"""Reading important geographical information from raster using GDAL.
	
	:param rast: Path to raster file in GDAL accepted format.
	:type rast: str
	
	:return gtransf: The affine transformation coefficients.
	:rtype gtransf: tuple
	:return prj: Projection information of the raster (dataset). 
	:rtype prj: str
	:return xSize: Pixel width (m).
	:rtype xSize: float
	:return ySize: Pixel heigth (m)
	:rtype ySize: float
	:return EPSG: EPSG Geodetic Parameter Set code.
	:rtype EPSG: int
	"""

	ds = gdal.Open(rast)
	gtransf = ds.GetGeoTransform()

	ds_s = ds.GetRasterBand(1)
	prj = ds.GetProjection()
	xSize = gtransf[1]
	ySize = gtransf[5] * (-1)

	srs = osr.SpatialReference(wkt=prj)
	if srs.IsProjected:
		EPSG = int(srs.GetAttrValue("authority", 1))
	else:
		EPSG = None

	ds = None

	return (gtransf, prj, xSize, ySize, EPSG)

def arrayToRast(arrays, names, prj, gtransf, EPSG, out_folder,
                out_file_name=None, driver_name="GTiff", multiband=False):
	"""Export numpy 2D arrays to multiband or singleband raster files. Following
	common raster formats are accepted for export:
	\n
	- ENVI .hdr labeled raster format
	- Erdas Imagine (.img) raster format
	- Idrisi raster format (.rst) 
	- TIFF / BigTIFF / GeoTIFF (.tif) raster format
	- PCI Geomatics Database File (.pix) raster format
	
	**Required inputs**
	:param arrays: Numpy array or list of arrays for export to raster.
	:type arrays: numpy.ndarray or list of numpy.ndarray
	:param names: Name or list of names of the exported bands (in case
		of multiband raster) or particular rasters (in case of singleband
		rasters).
	:type names: str or list of str
	:param prj: Projection information of the exported raster (dataset).
	:type prj: str
	:param gtransf: The affine transformation coefficients.
	:type gtransf: tuple
	:param EPSG: EPSG Geodetic Parameter Set code.
	:type EPSG: int
	:param out_folder: Path to folder where the raster(s) will be created.
	:type out_folder: str
	
	**Optional inputs**
	:param driver_name: GDAL driver. 'GTiff' is default.
	:type driver_name: str
	:param out_file_name: Name of exported multiband raster. Default is None.
	:type out_file_name: str
	:param multiband: Option of multiband raster creation. Default is False.
	:type multiband: bool
	
	**Returns**
	:returns: Raster singleband or multiband file(s)
	:rtype: raster
	"""

	# Convert arrays and names on list
	if type(arrays) is not list:
		arr_list = []
		arr_list.append(arrays)
		arrays = arr_list
	if type(names) is not list:
		names_list = []
		names_list.append(names)
		names = names_list

	if out_file_name is None:
		out_file_name = ""
		multiband = False

	# Drivers and suffixes
	driver_list = ["ENVI", "HFA", "RST", "GTiff",
	               "PCIDSK"]  # GDAL driver for output files
	out_suffixes = ["", ".img", ".rst", ".tif",
	                ".pix"]  # Suffixes of output names

	# Test driver
	if driver_name not in driver_list:
		raise ValueError("Unknown driver. Data could not be exported.")

	driver_index = driver_list.index(driver_name)
	suffix = out_suffixes[driver_index]

	if multiband == True and driver_name != "RST":
		out_file_name, ext = os.path.splitext(out_file_name)
		out_file = os.path.join(out_folder, out_file_name + suffix)

		try:
			driver = gdal.GetDriverByName(driver_name)
			ds = driver.Create(out_file, arrays[0].shape[1], arrays[0].shape[0],
			                   len(arrays), gdal.GDT_Float32)
			ds.SetProjection(prj)
			ds.SetGeoTransform(gtransf)
			if EPSG is not None:
				outRasterSRS = osr.SpatialReference()
				outRasterSRS.ImportFromEPSG(EPSG)
				ds.SetProjection(outRasterSRS.ExportToWkt())
			j = 1
			for i in arrays:
				ds.GetRasterBand(j).WriteArray(i)
				ds.GetRasterBand(j).SetDescription(names[j - 1])
				ds.GetRasterBand(j).SetMetadataItem("Band name", names[j - 1])
				ds.GetRasterBand(j).FlushCache()
				j = j + 1
			ds = None
		except:
			raise Exception("Raster file %s has not been created." % (
						out_file_name + suffix))

	else:
		for i in range(0, len(arrays)):
			try:
				out_file_name, ext = os.path.splitext(names[i])
				out_file = os.path.join(out_folder, out_file_name + suffix)
				driver = gdal.GetDriverByName(driver_name)
				ds = driver.Create(out_file, arrays[i].shape[1],
				                   arrays[i].shape[0], 1, gdal.GDT_Float32)
				ds.SetProjection(prj)
				ds.SetGeoTransform(gtransf)
				if EPSG is not None:
					outRasterSRS = osr.SpatialReference()
					outRasterSRS.ImportFromEPSG(EPSG)
					ds.SetProjection(outRasterSRS.ExportToWkt())
				ds.GetRasterBand(1).WriteArray(arrays[i])
				ds.GetRasterBand(1).SetDescription(names[i])
				ds.GetRasterBand(1).SetMetadataItem("Band name", names[i])
				ds.GetRasterBand(1).FlushCache()
				ds = None
			except:
				raise Exception("Raster file %s has not been created." % (
							names[i] + suffix))
	return


def readLatLong(rast_path):
	"""Automatic setting of the lyrs coordinates according to the
	projection of NIR band in to the form."""

	inputEPSG = None

	if rast_path == "" or rast_path is None:
		raise IOError("Path to raster has not been set.")

	else:
		try:
			ds = gdal.Open(rast_path)
			gtransf = ds.GetGeoTransform()
			leftCornerX = gtransf[0]  # X position of left corner of the layer
			leftCornerY = gtransf[3]  # Y position of left corner of the layer
			xSize = gtransf[1]  # pixel X size
			ySize = gtransf[5]  # pixel Y size
			cols = ds.RasterXSize  # No. of columns
			rows = ds.RasterYSize  # No. of rows

			pointX = leftCornerX + (
						xSize * cols) / 2  # X position of the middle of the layer
			pointY = leftCornerY + (
						ySize * rows) / 2  # Y position of the middle of the layer

			prj = ds.GetProjection()

			ds = None

			# Spatial Reference System
			srs = osr.SpatialReference(wkt=prj)
			if srs.IsProjected:
				inputEPSG = int(srs.GetAttrValue("authority", 1))

			outputEPSG = int(4326)  # WGS84

			# create a geometry from coordinates
			point = ogr.Geometry(ogr.wkbPoint)
			point.AddPoint(pointX, pointY)

			# create coordinate transformation
			inSpatialRef = osr.SpatialReference()
			inSpatialRef.ImportFromEPSG(inputEPSG)

			outSpatialRef = osr.SpatialReference()
			outSpatialRef.ImportFromEPSG(outputEPSG)

			coordTransform = osr.CoordinateTransformation(inSpatialRef,
			                                              outSpatialRef)

			# transform point
			point.Transform(coordTransform)

			# Coords in EPSG 4326
			long_dec = point.GetX()
			lat_dec = point.GetY()

			return long_dec, lat_dec

		except IOError:
			raise IOError(
				"Latitude and longitude of the raster has not been calculated. Input raster probably has no geographical reference.")
