#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  Project: RadAgro
#  File: hydrIO.py
#
#  Author: Dr. Jakub Brom
#
#  Copyright (c) 2020. Dr. Jakub Brom, University of South Bohemia in
#  České Budějovice, Faculty of Agriculture.
#
#  This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>
#
#  Last changes: 07.12.20 18:11
#
# Date: 2018/11/08
#
# Description:


import os

# imports
import numpy as np
from osgeo import gdal, osr, ogr
from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsVectorLayer, QgsField


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

	:returns: The tuple of important geographic information about a \
	raster. The tuple contains:
	\n
		* The affine transformation coefficients (tuple)
		* Projection information of the raster or dataset (str)
		* Size of pixel at X scale (float)
		* Size of pixel at Y scale (float)
		* EPSG Geodetic Parameter Set code (int)
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
	"""Export numpy 2D arrays to multiband or singleband raster
	files. Following common raster formats are accepted for export:
	\n

	* ENVI .hdr labeled raster format
	* Erdas Imagine (.img) raster format
	* Idrisi raster format (.rst)
	* TIFF / BigTIFF / GeoTIFF (.tif) raster format
	* PCI Geomatics Database File (.pix) raster format

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
	:param driver_name: GDAL driver. 'GTiff' is default.
	:type driver_name: str
	:param out_file_name: Name of exported multiband raster. Default is None.
	:type out_file_name: str
	:param multiband: Option of multiband raster creation. Default is False.
	:type multiband: bool
	
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
		except Exception:
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
			except Exception:
				raise Exception("Raster file %s has not been created." % (
							names[i] + suffix))
	return


def readLatLong(rast_path):
	"""Automatic setting of the lyrs coordinates according to the
	projection of NIR band in to the form.

	:param rast_path: Raster path.

	:return: Longitude and latitude in decimal scale
	"""

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

			coordTransform = osr.CoordinateTransformation(
				inSpatialRef, outSpatialRef)

			# transform point
			point.Transform(coordTransform)

			# Coords in EPSG 4326
			long_dec = point.GetX()
			lat_dec = point.GetY()

			return long_dec, lat_dec

		except IOError:
			raise IOError("Latitude and longitude of the raster has"
						  "not been calculated. Input raster probably "
						  "has no geographical reference.")


def joinLyrWithDataFrame(in_layer_path, df_data, out_layer_path):
	"""
	Create GeoPackage layer from input vector data for crops and data
	of radioactive contamination stored in pandas dataframe.

	:param in_layer_path: Path to original input vector layer which is \
	used as a template for a new layer.
	:type in_layer_path: str
	:param df_data: Joining Pandas dataframe corresponding with \
	vector_layer. FID values must be equal.
	:type df_data: Pandas DataFrame
	:param out_layer_path: Path to output vector file.
	:type out_layer_path: str
	"""

	# Translate input layer to gpkg format and create new vector 
	# instance
	os.system("ogr2ogr -f GPKG -nln 'Radioactive contamination' " +
			  out_layer_path + " " + in_layer_path)

	vector_layer = QgsVectorLayer(out_layer_path, "New_layer", "ogr")

	# Remove all columns
	count = vector_layer.fields().count()
	ind_list = list(range(0, count))
	vector_layer.dataProvider().deleteAttributes(ind_list)
	vector_layer.updateFields()

	# Add new fields from df
	no_cols = df_data.shape[1]
	field_names = list(df_data.columns)
	field_names[0] = "fid2"

	fields_list = [QgsField(field_names[1], QVariant.String),
				   QgsField(field_names[2], QVariant.Double),
				   QgsField(field_names[3], QVariant.LongLong),
				   QgsField(field_names[4], QVariant.String)]

	for i in range(5,no_cols):
		fields_list.append(QgsField(field_names[i], QVariant.Double))

	vector_layer.dataProvider().addAttributes(fields_list)
	vector_layer.updateFields()

	# Get FID data from vector layer
	fid = []
	for feature in vector_layer.getFeatures():
		fid.append(feature.id())

	# Get data from Pandas df and add them to layer
	vector_layer.startEditing()
	for i in range(len(fid)):
		# Get data form df - index i is from 1
		features_data = list(df_data.iloc[i, :])[1::]

		# Set data to vector layer
		for j in range(len(features_data)):
			vector_layer.changeAttributeValue(
				fid[i], j+1, str(features_data[j]))

	vector_layer.commitChanges()

	return
