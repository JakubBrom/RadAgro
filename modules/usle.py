#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  Project: RadAgro
#  File: usle.py
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
#  Last changes: 06.12.20 16:15
#
#  Begin: 2018/11/19
#
#  Description: Calculation of soil loss using USLE equation.


# Imports

import os
import shutil
import tempfile

import pandas as pd
import numpy as np

from .hydrIO import *
from .waterflow import WaterBalance
from .zonal_stats import *

wb = WaterBalance()


class RadUSLE:
	"""Calculation of USLE"""

	def __init__(self):
		return
		
	@staticmethod
	def slope(dmt, x_size=1, y_size=1):
		"""
		Slope of terrain calculation (degrees)
		
		:param dmt: Digital elevation model.
		:type dmt: Numpy array
		:param x_size: Size of pixel in x axis (m)
		:type x_size: float
		:param y_size: Size of pixel in y axis (m)
		:type y_size: float
		
		:return: Slope of terrain (DMT) in degrees
		:rtype: Numpy array
		"""
		
		x, y = np.gradient(dmt)
		slope = np.arctan(np.sqrt((x/(x_size)) ** 2.0 + (y / (
			y_size)) ** 2.0)) * 180/np.pi
	
		# Replacing nan values to 0 and inf to value
		slope = np.nan_to_num(slope)
		del x
		del y
		
		return slope
		
	def fLS(self, dmt_path, crops_lyr_path=None, m=0.4, n=1.4):
		"""
		Combined factor of slope length and slope steepness factor
		of USLE.
		
		:param dmt_path: Path to DMT raster.
		:type dmt_path: str
		:param crops_lyr_path: Path to vector for calculation of zonal
		statistics.
		:type crops_lyr_path: str
		:param m: Exponent representing the Rill-to-Interrill Ratio.
		Default m = 0.4
		:type m: float
		:param n: Constant. Default n = 1.4
		:type n: float
		
		:return: Combined factor of slope length and slope steepness
		factor of USLE. If the vector_path is none the method returns
		Numpy array matrix of LS factor corresponding to input DMT
		raster layer. If a vector layer is used the zonal statistic
		is calculated for each polygon of the vector layer. Output is
		pandas dataframe containing FIDs of original vector and LS
		medians.
		:rtype: Numpy array or Pandas DataFrame
		"""

		# Dividing by zero is ignored
		ignore_zero = np.seterr(all = "ignore")

		# Check the crops vector path
		try:
			crops_path = os.path.abspath(
				crops_lyr_path).split("|")[0]
		except Exception:
			crops_path = crops_lyr_path

		# Read the DMT raster to Numpy array
		dmt = rasterToArray(dmt_path)
		gtransf, prj, xSize, ySize, EPSG = readGeo(dmt_path)

		# Flow accumulation probability layer calculation
		flowac = wb.flowAccProb(dmt, xSize, ySize)

		# Slope calculation
		slope = self.slope(dmt, xSize, ySize)

		# LS calculation
		ls_factor = n * (flowac * xSize/22.1)**m * (np.sin((slope *
													np.pi/180)/0.09))**n

		ls_factor = np.nan_to_num(ls_factor)

		# Calculate zonal stats of LS for fields in vector layer
		if crops_path is not None:
			# Paths handling
			# ls_dir = os.path.dirname(dmt_path)
			# ls_name = "LS_factor.tif"
			# ls_path = os.path.join(ls_dir, ls_name)

			# Make temporary folder
			tmp_folder = None
			try:
				# Create temporal folder
				tmp_folder = tempfile.mkdtemp()

				# Create path of temporal raster file
				tmp_file = tempfile.NamedTemporaryFile(
					suffix=".tif", dir=tmp_folder, delete=False)
				ls_path = tmp_file.name
				ls_name = os.path.basename(ls_path)
				ls_dir = os.path.dirname(ls_path)

			except OSError as err:
				raise err

			# Convert array of LS to raster
			arrayToRast(ls_factor, ls_name, prj, gtransf, EPSG,
						ls_dir)

			# Calculate zonal stats
			ls_factor = pd.DataFrame(zonal_stats(crops_path,
												 ls_path, "median"))
			ls_factor = ls_factor.fillna(0)

		# Remove data from memory
		del flowac
		del slope
		del dmt
		if tmp_folder is not None:
			shutil.rmtree(tmp_folder)

		return ls_factor

	@staticmethod
	def fR(r_const=40, month_perc=32.2):
		"""
		R factor of USLE for monthly data.

		:param r_const: Constant year value of R factor for particular
						area (MJ/ha)
		:type r_const: float
		:param month_perc: Percentage of R for particular months.
		:type month_perc: float

		:return: R value for particular month.
		:rtype: float
		"""
		
		r_factor = r_const * month_perc / 100

		return r_factor

	@staticmethod
	def fK(soil_units_lyr_path, soil_units_field_name, k_data,
		   crops_lyr_path, x_size=30, y_size=30):
		"""
		K erosivity factor of USLE.

		:param soil_units_lyr_path: Path to vector layer with Main
		soil units codes (HPJ - hlavní půdní jednotky, after Janeček
		et al. 2007).
		:type soil_units_lyr_path: str
		:param soil_units_field_name: Name of vector attribute field
		with Main soil units.
		:type soil_units_field_name: str
		:param k_data: Numpy dataframe containing K values with
		corresponding Main soil units which are used as IDs.
		:type k_data: Pandas DataFrame
		:param crops_lyr_path: Path to vector layer which is used
		for calculation of zonal statistics. FID values are used in
		output.
		:type crops_lyr_path: str
		:param x_size: Size of newly created raster resolution
		:type x_size: float
		:param y_size: Size of newly created raster resolution
		:type y_size: float

		:return: Pandas dataframe containing FIDs corresponding to
		vector layer used for zonal statistics calculation and K
		factor values for each field/polygon
		:rtype: Pandas DataFrame
		"""

		# Check the soil vector path
		try:
			su_lyr_path = os.path.abspath(
				soil_units_lyr_path).split("|")[0]
		except Exception:
			su_lyr_path = soil_units_lyr_path

		# Check the crops vector path
		try:
			crops_path = os.path.abspath(
				crops_lyr_path).split("|")[0]
		except Exception:
			crops_path = crops_lyr_path

		# Get name of layer used for rasterization
		try:
			su_file_name = os.path.basename(soil_units_lyr_path).split(
							"=")[1]
		except Exception:
			su_file_name = ""

		if su_file_name == "":
			su_file_name = os.path.basename(soil_units_lyr_path).split(
				".")[0]

		# Make temporary folder
		tmp_folder = None
		try:
			# Create temporal folder
			tmp_folder = tempfile.mkdtemp()

			# Create path of temporal raster file
			tmp_file = tempfile.NamedTemporaryFile(
				suffix=".tif", dir=tmp_folder, delete=False)
			soil_units_raster_path = tmp_file.name

		except OSError as err:
			raise err

		# Rasterize
		os.system("gdal_rasterize -a {su_field} -tr {x_size} "
				"{y_size} -l {su_name} {su_path} {su_rast}".format(
					su_field=soil_units_field_name, x_size=x_size,
					y_size=y_size, su_name=su_file_name,
					su_path=su_lyr_path,
					su_rast=soil_units_raster_path))

		# Zonal stats by crops layer --> pandas df
		df_soil_units = pd.DataFrame(zonal_stats(crops_path,
												 soil_units_raster_path,
												 "mode"))
		df_soil_units = df_soil_units.astype(int)

		# Join K values to HPJ column and make new df with K values
		# Get names of keys
		k_id_name = k_data.columns[0]
		su_id_name = df_soil_units.columns[1]

		# Merge dfs
		df_merge = pd.merge(df_soil_units, k_data, how="left",
							left_on=su_id_name, right_on=k_id_name)

		# Create new df for K factor values
		k_factor = pd.DataFrame({"FID":df_merge.iloc[:,0]})
		k_factor["k_value"] = df_merge.iloc[:,3]
		k_factor = k_factor.fillna(0)

		# Clear tmp and memory
		del df_soil_units
		del df_merge

		if tmp_folder is not None:
			shutil.rmtree(tmp_folder)

		return k_factor
