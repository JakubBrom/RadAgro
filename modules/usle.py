#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#-----------------------------------------------------------------------
# RadHydro 
#
# Module: usle.py
#
# Author: Jakub Brom, University of South Bohemia in Ceske Budejovice,
#		  Faculty of Agriculture 
#
# Date: 2018/11/19
#
# Description: Calculation of soil loss using USLE equation.
# 
# License: Copyright (C) 2018, Jakub Brom, University of South Bohemia
#		   in Ceske Budejovice
# 
# Vlastníkem programu RadHydro je Jihočeská univerzita v Českých 
# Budějovicích. Všechna práva vyhrazena. Licenční podmínky jsou uvedeny
# v licenčním ujednání (dále jen "smlouva").
# Uživatel instalací nebo použitím programu, jeho verzí nebo aktualizací
# souhlasí s podmínkami smlouvy.
#-----------------------------------------------------------------------


# Imports

import numpy as np


class RadUSLE:
	"""Calculation of USLE"""

	def __init__(self):
		return
		
	def usle(self, R, K, LS, C, P=1):
		"""
		Universal Soil Loss Equation.

		Inputs:
		:param R: R erosivity factor of USLE.
		:type R: Numpy array (float)
		:param K: K erodibility factor of USLE.
		:type K: Numpy array (float)
		:param LS: Combined factor of slope length and slope steepness
				   factor of USLE.  
		:type LS: Numpy array (float)
		:param C: C cover management impact factor of USLE.
		:type C: Numpy array (float)
		:param P: P support practices factor of USLE.
		:type P: Numpy array (float) or float.

		Returns:
		:return: Spatial and temporal soil loss (t/ha). Here,
				   the equation is calculated for monthly data.
		:rtype: Numpy array (float)
		"""

		# Inputs:
		if R is None:
			raise IOError("Error: R factor has not been calculated! Calculation has been terminated.")
		if K is None:
			raise IOError("Error: K factor has not been calculated! Calculation has been terminated.")
		if LS is None:
			raise IOError("Error: LS factor has not been calculated! Calculation has been terminated.")
		if C is None:
			raise IOError("Error: C factor has not been calculated! Calculation has been terminated.")
		if P is None:
			raise IOError("Error: P factor has not been calculated! Calculation has been terminated.")

		# Wischmeier & Smith USLE equation 
		G = R * K * LS * C * P

		# Replace nans to 0
		G_mask = np.isnan(G)
		G[G_mask] = 0

		return G
		
	def slope(self, dmt, xSize = 1, ySize=1):
		"""
		Function calculates slope of terrain (DMT) in degrees
		
		Inputs:
		:param dmt: Digital elevation model.
		:type dmt: Numpy array
		:param xSize: Size of pixel in x axis (m)
		:type xSze: float
		:param ySize: Size of pixel in y axis (m)
		:type ySize: float
		
		Returns: float
		:return slope: Slope of terrain (DMT) in degrees
		:rtype slope: Numpy array
		"""
		
		x, y = np.gradient(dmt)
		slope = np.arctan(np.sqrt((x/(xSize))**2.0 + (y/(ySize))**2.0))*180/np.pi
	
		# Replacing nan values to 0 and inf to value
		slope = np.nan_to_num(slope)
		del x
		del y
		
		return slope
		
	def fLS(self, flowac, slope, xSize=1, m=0.4, n=1.4):
		"""
		Combined factor of slope length and slope steepness factor
		of USLE.
		
		Inputs:
		:param flowac: Flow accumulation probability grid.
		:type flowac: Numpy array
		:param slope: Slope grid (degrees)
		:type slope: Numpy array
		:param xSize: Size of pixel (m)
		:type xSize: float
		:param m: Exponent representing the Rill-to-Interrill Ratio.
				  Default m = 0.4
		:type m: float
		:param n: Constant. Default n = 1.4
		:type n: float
		
		Returns:
		:return LS: Combined factor of slope length and slope steepness
					factor of USLE
		:rtype LS: Numpy array
		"""
		
		# Inputs
		if flowac is None:
			raise IOError("Error: Flow accumulation probability grid has not been calculated! Calculation has been terminated.")
		if slope is None:
			raise IOError("Error: Slope grid has not been calculated! Calculation has been terminated.")

		# LS calculation
		LS = n * (flowac * xSize/22.1)**m * (np.sin((slope * np.pi/180)/0.09))**n
		
		return LS

	def fR(self, R_const = 40, month_perc=32.2):
		"""
		R erosivity factor of USLE for monthly data.

		Inputs:
		:param R_const: Constant year value of R factor for particular
						area (MJ/ha)
		:type R_const: float
		:param month_perc: Percentage of R for particular months.
		:type month_perc: float

		Returns:
		:return R: R value for particular month.
		:rtype R: float
		"""
		
		R = R_const * month_perc/100

		return R

	def fK(self, HPJ, k_values):
		"""
		K erodibility factor of USLE.

		Inputs:
		:param HPJ: Numpy array with Main soil units codes (HPJ - hlavní
					půdní jednotky, after Janeček et al. 2007).
		:type HPJ: Numpy array, int
		:param k_values: K values corresponding to Main soil units
		codes are set according to Janeček et al. (2007)
		:type k_values: list

		Returns:
		:return K_matrix: Matrix of K values.
		:rtype K_matrix: Numpy array, float
		"""

		# Input handling
		if HPJ is None:
			raise IOError("Error: Main soil units data are not available! Calculation has been terminated.")
		HPJ = HPJ.astype(int)

		# Join matrix of HPJ data with K values
		for i in range(len(k_values)):
			j = i+1
			K_matrix = np.where(HPJ == j, k_values[i], np.isnan(True))

		return K_matrix

	def fC(self, crops, c_values):
		"""
		Crop factor of USLE.

		:param crops: Layer with codes of C factor for particular crops.
					  The codes are following: 
		
						Crops:
						1: winter wheat
						2: spring wheat
						3: winter rye
						4: spring barley
						5: winter barley
						6: oat
						7: maize (corn)
						8: legumes
						9: early potatoes
						10: late potatoes
						11: meadows
						12: hoppers
						13: winter rape
						14:	sunflower
						15: poppy
						16: another oilseeds
						17:	maize (silage)
						18: another one-year-olds fodder crops
						19: another perenial fodder crops
						20:	vegetables
						21: orchards
						22: forests
						23: municipalities
						24: bare soil

		:type crops: Numpy array (int)
		:param c_values: C values corresponding to crop categories
		are set according to Janeček et al. (2007)
		:type c_values: list

		Returns:
		:return: Matrix of C values.
		:rtype: Numpy array (float)
		"""
		
		# Input handling
		if crops is None:
			raise IOError("Error: Main soil units data are not available! Calculation has been terminated.")
		crops = crops.astype(int)

		# Join matrix of HPJ data with K values
		for i in range(len(c_values)):
			j = i+1
			C_matrix = np.where(crops == j, c_values[i], np.isnan(True))

		return C_matrix
