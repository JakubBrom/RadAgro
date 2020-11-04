#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#-----------------------------------------------------------------------
# RadHydro 
#
# Module: surrunoff.py
#
# Author: Jakub Brom, University of South Bohemia in Ceske Budejovice,
#		  Faculty of Agriculture 
#
# Date: 2018/11/08
#
# Description:
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


# imports
import numpy as np
import math as mt
import warnings
from mdaylight import MonthlyDaylight


class WaterBalance:
	"""Module for calculation of the hydrological features of the area of
	interest."""

	def __init__(self):
		return

	def airTemperToGrid(self, tm_list, dmt, altitude, adiab=0.65):
		"""
		Calculation of spatial temperature distribution in accordance
		to altitude (DEM). The function provides list (Numpy array) of air
		temperature arrays corresponding to list of measured temperature
		data.
		
		Inputs:
		:param tm_list: List of air temperatures measured on a meteostation.
		:type tm_list: list
		:param dmt: Digital elevation model.
		:type dmt: Numpy array
		:param altitude: Altitude of temperature measurement.
		:type altitude: float
		:param adiab: Adiabatic change of temeperature with altitude
					  per 100 m. Default value is 0.65 °C/100 m.
		:type adiab: float
		
		Returns:
		:return tm_grids: List of air temperature grids.
		:rtype tm_grids: Numpy array
		"""
		
		# Convert input temperature list to Numpy array
		tm_list = np.array(tm_list, dtype = float)
		
		# Replace temperature values lower to 1 to 1 --> Calculation of ET
		tm_list = np.where(tm_list < 1.0, 1.0, tm_list)
		
		# Create temperature grids
		tm_grids = [np.array(tm_list[i] + adiab/100 * (altitude - dmt), dtype = float) for i in range(0, len(tm_list))]
		tm_grids = np.array(tm_grids, dtype = float) # convert to np.array
		
		# Replace temperature values lower to 1 to 1
		tm_grids = np.where(tm_grids <= 1.0, 1.0, tm_grids)
		
		return tm_grids

	def evapoPot(self, tm_grids, lat = 49.1797903):
		"""
		Potential monthly ET According to Thornthwaite 1948. Script
		calculates ETpot for the whole year - for each month. 
		
		Inputs:
		:param tm_grids: List of monthly mean air temperatures during
		the year (degree of Celsius) - temperature normals
		:type tm_grids: list
		:param lat: Earth latitude (UTM) in decimal degrees
		:type lat: float
		
		Returns
		:return ET_pot: Potential monthly evapotranspiration according
		to Thornthwaite (1984), mm. List of monthly values for the year.
		:rtype ETpot_list: Numpy array
		"""
		
		# inputs
		n_days = np.array((31,28,31,30,31,30,31,31,30,31,30,31), dtype = np.float) # length of month
		md = MonthlyDaylight()
		dl = md.monthlyDaylights(lat)		# list of mean monthly daylights (dec. hour)
		dl = np.array(dl, dtype = float)
		
		# temperature grids manipulation
		tm_grids = np.array(tm_grids, dtype = np.float)
		tm_grids = np.where(tm_grids <= 0, 1.0, tm_grids) 
		
		# calculate constats:
		ij = (tm_grids/5)**1.514
		I = sum(ij)
		a = (0.0675 * I**3 - 7.71 * I**2 + 1792 * I + 47239) * 10**(-5)
	
		# calculate mean potential ET grids
		ETpot_list = [16 * dl[i]/12 * n_days[i]/30 * (10 * tm_grids[i]/I)**a for i in range(0, len(tm_grids))]
		
		return ETpot_list
	
	def evapoActual(self, ETp, precip):
		"""Actual evapotranspiration calculated according to Ol'dekop (1911,
		cited after Brutsaert (1992) and Xiong and Guo 
		(1999; doi.org/10.1016/S0022-1694(98)00297-2)
		
		Inputs:
		:param ETp: Potential monthly evapotranspiration according
		to Thornthwaite (1984), mm. List of monthly values for the year.
		:type ETp: list
		:param precip: Mean monthly precipitation throughout the year (mm).
		:type precip: list
		
		Returns
		:return ETa: Actual monthly evapotranspiration throughout the year (mm) 
		:rtype ETa: Numpy array
		"""
		
		ETp = np.array(ETp, dtype = float)
		precip = np.array(precip, dtype = float)
	
		ETa = ETp * np.tanh(precip/ETp)
		
		if ETa == None or ETa <= 0:
			warnings.warn("Warning: Evapotranspiration data contains NANs.", stacklevel=3)

		return ETa
	
	def interceptWater(self, precip, LAI, a=0.1, b=0.2):
		"""
		Interception of precipitation on the biomass and soil surface 
		for monthly precipitation data (mm)
		
		Inputs:
		:param precip: Grid of monthly mean precipitation amount (mm)
		:type precip: Numpy array
		:param LAI: Grid of monthly mean leaf area index (unitless)
		:type LAI: Numpy array
		:param a: Constant
		:type a: float
		:param b: Constant
		:type b: float
		
		Returns:
		:return I: Grid of amount of intercepted water during month (mm)
		:rtype I: Numpy array
		"""
		
		# Inputs
		precip = np.array(precip, dtype = float)
		LAI = np.array(LAI, dtype = float)
		
		# Calculation
		const = a * np.exp(b * LAI)
		I = const * precip
		
		return I
	
	def runoffSeparCN(self, acc_precip, ET, ETp, I, CN=65,  a=0.005, b=0.005, c=0.5):
		"""
		The script separates precipitation ammount (accumulated) into 
		surface runoff, water retention and evapotranspiration for
		monthly precipitation data. The method is based on the modified
		CN curve method.
		
		Inputs:
		:param acc_precip: Monthly mean of acc_precipitation (mm)
		:type acc_precip: float
		:param ET: Monthly mean evapotranspiration (mm)
		:type ET: float
		:param ETp: Monthly mean potential evapotranspiration (mm)
		:type ETp: float
		:param I: Amount of intercepted water during month (mm)
		:type I: float
		:param CN: Curve number
		:type CN: int
		:param a: Constant
		:type a: float
		:param b: Constant
		:type b: float
		:param c: Constant
		:type c: float
		:param d: Constant
		:type d: float
		:param e: Constant
		:type e: float
		
		Returns:
		:return Rcor: Amount of monthly surface runoff (mm) corrected on ET
		:rtype Rcor: float
		:return Scor: Amount of retention of water in the soil
				   or subsurface runoff (mm) corrected on ET
		:rtype Scor: float
		:return ETa: Monthly amount of actual evapotranspiration 
					 from the surface (mm)
		:rtype ETa: float
		"""

		# Constants
		const_a = mt.exp(-a * acc_precip)
		const_b = b * CN + c
		
		# Potentional retention in soil
		if CN == 101:							# for water bodies
			Smax = 0
			I = 0
		else:
			Smax = 25.4 * (1000/CN-10)
		
		# Surface runoff
		if acc_precip < 0.2 * Smax:
			R = 0.0

		else:
			R = (acc_precip - I)**2 / (acc_precip - I + Smax)

		# Retention
		S = acc_precip - I - R

		# Evapotranspiration
		ETa = const_a * R + const_b * S + I
		
		if ETa > ET:
			ETa = ET

		if CN == 101:							# for water bodies
			ETa = ETp

		# Correction of runoff and retention
		if ETa > acc_precip:				# ET higher than acc_precipitation
			Rcor = 0.0
			Scor = 0.0
			ETa = acc_precip
		else:
			## ET coefficients calculation (spliting ET):
			coef_R = const_a * R/(const_a * R + const_b * S)
			coef_S = 1 - coef_R
	
			# Surface runoff corrected on ET
			Rcor = R - (ETa - I) * coef_R
			
			# Retention corrected on ET
			Scor = S  - (ETa - I) * coef_S

		return Rcor, Scor, ETa

	def flowProbab(self, win_dmt, xsize=1.0, ysize=1.0):
		"""
		Calculation of probability of water flow direction in 3x3 matrix
		on basis of elevation data.
		
		Inputs:
		:param win_dmt: 3x3 matrix of elevation model.
		:type win_dmt: numpy array
		:param xsize: Size of pixel in x axis (m)
		:type xsize: float
		:param ysize: Size of pixel in y axis (m)
		:type ysize: float
		"""
		
		# Input data processing
		x,y = win_dmt.shape
		if x is not 3 or y is not 3:
			raise IOError("Error: Probability of water flow direction can not be calculated! Calculation has been terminated.")
		
		#find difference between lower cells and center cell
		diff = np.where(win_dmt < win_dmt[1,1], win_dmt[1,
													   1] - win_dmt, 0) # spocte rozdíl mezi centralni bunkou a hodnotami mensimi nez centralni bunka. Ostatni jsou 0 vcetne centralni
		
		# reseni plochych mist bez sklonu - predpokladem je vsesmerny odtok
		if diff.sum() == 0:
			diff = np.ones((3,3), dtype = float)
			diff[1,1] = 1
		else:
			# vypocet pravdepodobnosti odtoku do jednotlivych pixelu na zaklade geometrie (uhel sklonu) ==> uhel(alfa)/90 ==> pravdepodobnost se meni linearne se sklonem
			diff[0,1] = 2 * mt.atan(diff[0,1]/ysize)/mt.pi									#N
			diff[1,2] = 2 * mt.atan(diff[1,2]/xsize)/mt.pi									#E
			diff[2,1] = 2 * mt.atan(diff[2,1]/ysize)/mt.pi									#S
			diff[1,0] = 2 * mt.atan(diff[1,0]/xsize)/mt.pi									#W
			diff[0,2] = 2 * mt.atan(diff[0,2]/mt.sqrt(xsize**2 + ysize**2))/mt.pi			#NE
			diff[2,2] = 2 * mt.atan(diff[2,2]/mt.sqrt(xsize**2 + ysize**2))/mt.pi			#SE
			diff[2,0] = 2 * mt.atan(diff[2,0]/mt.sqrt(xsize**2 + ysize**2))/mt.pi			#SW
			diff[0,0] = 2 * mt.atan(diff[0,0]/mt.sqrt(xsize**2 + ysize**2))/mt.pi			#NW
		
		# pravdepodobnost odtoku do jednotlivych smeru. Suma pravdepodobnosti = 1.
		probab = diff/diff.sum()
		
		return probab

	def waterFlows(self, dmt, precip, CN, LAI, ETp, xsize=1.0, ysize=1.0, a=0.005, b=0.005, c=0.5, d=0.1, e=0.2):
		"""
		Calculation of flow accumulation according to digital elevation model.
		Probability of flow direction within DEM is calculated on basis 
		of shape of the surface (outflow changes linearly with changing angle
		between neighbour pixels) and surface resistance for surface runoff
		(rel.).
		The function was inspired by Multipath-Flow-Accumulation developed
		by Alex Stum: https://github.com/StumWhere/Multipath-Flow-Accumulation.git
		
		:param dmt: Digital elevation model of the surface (m).
		:type dmt: numpy.ndarray
		:param xsize: Size of pixel in x axis (m)
		:type xsize: float
		:param ysize: Size of pixel in y axis (m)
		:type ysize: float

		:param rs: Surface resistance wor surface runoff of water scaled
				   to interval <0; 1>, where 0 is no resistance
				   and 1 is 100% resistance (no flow). Scaled Mannings n
				   should be used. Default is None (zero resistance is used).
		:type rs: numpy.ndarray
		
		:return accum: Flow accumulation grid.
		:rtype accum: numpy.ndarray
		"""
	
		# dividing by zero is ignored
		ignore_zero = np.seterr(all = "ignore")
	
		# Handling input grids
		## DEM
		if dmt is None:
			raise IOError("Error: Elevation data are not available! Calculation has been terminated.")
		dmt = np.array(dmt, dtype = float)
		## Precipitation
		if precip is None:
			raise IOError("Error: Precipitation data are not available! Calculation has been terminated.")
		precip = np.array(precip, dtype = float)
		##CN curves
		if CN is None:
			raise IOError("Error: CN curves layer is not available! Calculation has been terminated.")
		CN = np.array(CN, dtype = float)
		##LAI - leaf area index
		if LAI is None:
			raise IOError("Error: Leaf area index data are not available! Calculation has been terminated.")
		LAI = np.array(LAI, dtype = float)
		##ETp - potential ET
		if ETp is None:
			raise IOError("Error: Potential evapotranspiration data are not available! Calculation has been terminated.")
		ETp = np.array(ETp, dtype = float)

		## Fill NANs by mean of neighbour values in raster (by rows)
		if np.isnan(np.sum(dmt)) == True:
			mask = np.isnan(dmt)
			dmt[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(~mask), dmt[~mask])
			warnings.warn("Warning: The elevation data contains NANs. NANs has been filled.", stacklevel=3)
	
		# Preparation DEM data
		dmt_flat = dmt[1:-1,1:-1].flatten("F")		# prevedeni na radu podle sloupcu (Fortran styl) --> je to asi jedno. Hodnoty jsou orizle o okrajove bunky.
		index_dmt = np.argsort(dmt_flat,axis=0,kind='mergesort')	# usporadani hodnot podle vyskopisu --> od nejmensi po nejvetsi hodnotu. Algoritmus vraci indexy pozice hodnot v puvodnim souboru.

		# Preparation of intercept
		interc = self.interceptWater(precip, LAI, d, e)
		
		# Preparation of accumulation layers
		surf_acc = np.zeros_like(dmt).astype(float)		# startovni vrstva akumulace povrchoveho odtoku
		subsurf_acc = np.zeros_like(dmt).astype(float)	# startovni vrstva akumulace podpovrchoveho odtoku 
		ET_acc = np.zeros_like(dmt).astype(float)		# startovni vrstva aktualniho vyparu 

		nrows=dmt.shape[0]-2		# pocet sloupcu a radku bez okrajovych
		
		# Calculation of precip. water accumulation
		for i in index_dmt[::-1]:		# postupuje podle indexu v poradi od nejvetsi do nejmensi hodnoty
			
			#define position of calculation window
			y=int(i%nrows)		# vrati zbytek po deleni
			x=int(i/nrows)		# 

			# create 3x3 windows for calculation
			win_dmt = dmt[y:y+3,x:x+3] 			# vyreze matice 3x3 z dmt v poradi podle index_dmt
			
			# calculate probability of water flow
			probab = self.flowProbab(win_dmt, xsize, ysize)
			
			# Surface and subsurface runoff, ETa
			total_water = surf_acc[y+1,x+1] + precip[y+1,x+1] 	# celkovy uhrn vody, ktera muze nekam odtekat
			ET = self.evapoActual(ETp[y+1,x+1], total_water)	# evapotranspiration
						
			# Flows after correction
			Rcor, Scor, ETa = self.runoffSeparCN(total_water, ET, ETp[y+1,x+1], interc[y+1,x+1], CN[y+1,x+1], a=a, b=b, c=c)

			# Calculation proportions of water flows from precipitation
			surfrun = (precip[y+1,x+1] - ETa) * (Rcor/(total_water - ETa))
			subrun = (precip[y+1,x+1] - ETa) * (Scor/(total_water - ETa))
			if surfrun <= 0:
				surfrun = 0
			if subrun <= 0:
				subrun = 0

			#proportionally distribute
			surf_acc[y:y+3,x:x+3] += probab * (surf_acc[y+1,x+1] + surfrun)		# akumulace povrchoveho odtoku
			subsurf_acc[y:y+3,x:x+3] += probab * (subsurf_acc[y+1,x+1] + subrun)	# akumulace podpovrchoveho odtoku
			ET_acc[y+1, x+1] += ETa												# ETa
			
			# Adding part of precipitation to central cell
			surf_acc[y+1,x+1] += surfrun
			subsurf_acc[y+1,x+1] += subrun
			
		#accum = np.nan_to_num(accum)
		acc_mask = np.isnan(surf_acc)
		surf_acc[acc_mask] = 0
		acc_mask = np.isnan(subsurf_acc)
		subsurf_acc[acc_mask] = 0
		acc_mask = np.isnan(ET_acc)
		ET_acc[acc_mask] = 0
		
		return surf_acc, subsurf_acc, ET_acc
	
	def flowAccProb(self, dmt, xsize=1.0, ysize=1.0, rs=None):
		"""
		Calculation of flow accumulation probability layer according
		to digital elevation model. Probability of flow direction within
		DEM is calculated on basis of shape of the surface (outflow
		changes linearly with changing angle between neighbour pixels) 
		and surface resistance for surface runoff (rel.).
		The function was inspired by Multipath-Flow-Accumulation developed
		by Alex Stum: https://github.com/StumWhere/Multipath-Flow-Accumulation.git
		
		:param dmt: Digital elevation model of the surface (m).
		:type dmt: numpy.ndarray
		:param xsize: Size of pixel in x axis (m)
		:type xsize: float
		:param ysize: Size of pixel in y axis (m)
		:type ysize: float
		:param rs: Surface resistance wor surface runoff of water scaled
				   to interval <0; 1>, where 0 is no resistance
				   and 1 is 100% resistance (no flow). Scaled Mannings n
				   should be used. Default is None (zero resistance is used).
		:type rs: numpy.ndarray
		
		:return accum: Flow accumulation grid.
		:rtype accum: numpy.ndarray
		"""
	
		# dividing by zero is ignored
		ignore_zero = np.seterr(all = "ignore")
	
		# Handling dmt data
		if dmt is None:
			raise IOError("Error: Elevation data are not available! Calculation has been terminated.")
		
		## Fill NANs by mean of neighbour values in raster (by rows)
		if np.isnan(np.sum(dmt)) == True:
			mask = np.isnan(dmt)
			dmt[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(~mask), dmt[~mask])
			warnings.warn("Warning: The elevation data contains NANs. No data has been filled.", stacklevel=3)
	
		# Handling surface resistance
		if rs is None:
			rs = np.zeros_like(dmt).astype(float)		# zero resistance is default
		
		## Fill NANs by 0
		if np.isnan(np.sum(rs)) == True:
			rs = np.nan_to_num(rs)
			warnings.warn("Warning: The surface resistance data contains NANs. No data has been filled.", stacklevel=3)
		
		## Trimm values of rs to interval <0,1> 
		if np.max(rs) > 1 or np.min(rs) < 0:
			warnings.warn("Warning: The surface resistance data contains values out of required interval!\nValues out of interval <0; 1> were replaced either by 1 if the values are bigger than 1\n or by 0 if the values are lower than 0", stacklevel=3)
			rs = np.where(rs > 1, 1, rs)
			rs = np.where(rs < 0, 0, rs)
		
		## All values of rs are bigger than 1
		if np.mean(rs) >= 1:
			raise ValueError("Error: Flow accumulation can not be calculated! Surface resistance does not allow runoff.")
		
		## Control of spatial extent
		if rs.shape[0] != dmt.shape[0] or rs.shape[1] != dmt.shape[1]:
			raise ValueError("Error: Flow accumulation can not be calculated! Spatial extent of digital elevation model and surface resistance layer does not match.")
		
		# Preparation DEM data
		dmt_flat = dmt[1:-1,1:-1].flatten("F")		# prevedeni na radu podle sloupcu (Fortran styl) --> je to asi jedno. Hodnoty jsou orizle o okrajove bunky.
		index_dmt = np.argsort(dmt_flat,axis=0,kind='mergesort')	# usporadani hodnot podle vyskopisu --> od nejmensi po nejvetsi hodnotu. Algoritmus vraci indexy pozice hodnot v puvodnim souboru.
		accum = np.ones_like(dmt).astype(float) #* precip		# startovni vrstva akumulace odtoku --> predpoklada jednickovy odtok

		nrows=dmt.shape[0]-2		# pocet sloupcu a radku bez okrajovych
		
		# Calculation of precip. water accumulation
		for i in index_dmt[::-1]:		# postupuje podle indexu v poradi od nejvetsi do nejmensi hodnoty
			
			
			#define position of calculation window
			y=int(i%nrows)		# vrati zbytek po deleni
			x=int(i/nrows)		# 

			# create 3x3 windows for calculation
			win_dmt = dmt[y:y+3,x:x+3] 			# vyreze matice 3x3 z dmt v poradi podle index_dmt
			win_rs = rs[y:y+3,x:x+3]			# vyrez matice 3x3 z odporu povrchu pro odtok (něco jako Manning: hodnoty v intervalu <0, 1>, kde 0 => zadny odpor, 1 => blokovany odtok)

			#find difference between lower cells and center cell
			diff=np.where(win_dmt < win_dmt[1,1], win_dmt[1,1] - win_dmt, 0) # spocte rozdíl mezi centralni bunkou a hodnotami mensimi nez centralni bunka. Ostatni jsou 0 vcetne centralni

			# reseni plochych mist bez sklonu - predpokladem je vsesmerny odtok
			if diff.sum() == 0:
				diff = np.ones((3,3), dtype = float)
				diff[1,1] = 0
			else:
				# vypocet pravdepodobnosti odtoku do jednotlivych pixelu na zaklade geometrie (uhel sklonu) ==> uhel(alfa)/90 ==> pravdepodobnost se meni linearne se sklonem
				diff[0,1] = 2 * mt.atan(diff[0,1]/ysize)/mt.pi									#N
				diff[1,2] = 2 * mt.atan(diff[1,2]/xsize)/mt.pi									#E
				diff[2,1] = 2 * mt.atan(diff[2,1]/ysize)/mt.pi									#S
				diff[1,0] = 2 * mt.atan(diff[1,0]/xsize)/mt.pi									#W
				diff[0,2] = 2 * mt.atan(diff[0,2]/mt.sqrt(xsize**2 + ysize**2))/mt.pi			#NE
				diff[2,2] = 2 * mt.atan(diff[2,2]/mt.sqrt(xsize**2 + ysize**2))/mt.pi			#SE
				diff[2,0] = 2 * mt.atan(diff[2,0]/mt.sqrt(xsize**2 + ysize**2))/mt.pi			#SW
				diff[0,0] = 2 * mt.atan(diff[0,0]/mt.sqrt(xsize**2 + ysize**2))/mt.pi			#NW
			
			# Application of surface resistance on probability of runoff accumulation
			prob_pix = diff * (1 - win_rs)
			
			# pravdepodobnost odtoku do jednotlivych smeru. Suma pravdepodobnosti = 1.
			probab = prob_pix/prob_pix.sum()
			
			#proportionally distribute
			accum[y:y+3,x:x+3] += probab * accum[y+1,x+1]	# pripocte ke stavajici matici accum pravdepodobnosti odtoku. Pravdepodobnost dtoku se nasobi uhrnem srazek (pro centralni bunku)
															# accum[y+1,x+1] je suma srazek z predchoziho vypoctu
		
		#accum = np.nan_to_num(accum)
		acc_mask = np.isnan(accum)
		accum[acc_mask] = 1.0
	
		return accum

	# def estimateCN(self, HPJ, crop, IPS=2):
	# 	"""Define CN curves according to main soil units (HPJ) and crop
	# 	classes. The estimation is rough, based on averaging values for
	# 	different conditions.
	#
	# 	:param HPJ: Main Soil Unit. Based on Czech national soil
	# 	classification (BPEJ).
	# 	:type HPJ: Numpy ndarray, float
	# 	:param crop: Layer with codes of C factor for particular crops.
	# 				  The codes are following:
	#
	# 					Crops:
	# 					1: winter wheat
	#					3: spring wheat
	# 					2: winter rye
	# 					3: spring barley
	# 					4: winter barley
	# 					5: oat
	# 					6: maize (corn)
	# 					7: legumes
	# 					8: early potatoes
	# 					9: late potatoes
	# 					10: meadows
	# 					11: hoppers
	# 					12: winter rape
	# 					13:	sunflower
	# 					14: poppy
	# 					15: another oilseeds
	# 					16:	maize (silage)
	# 					17: another one-year-olds fodder crops
	# 					18: another perenial fodder crops
	# 					19:	vegetables
	# 					20: orchards
	# 					21: forests
	# 					22: municipalities
	# 					23: bare soil
	#
	# 	:type crop: Numpy ndarray, int
	# 	:param IPS: The state of hydrological status of the soil.
	# 	\n
	# 	IPS = 1 -> Dry soil
	# 	IPS = 2 -> Mean saturation of soil
	# 	IPS = 3 -> Wet saturated soil
	# 	\n
	# 	Default value is IPS = 2 (constant for whole area).
	# 	:type IPS: Numpy ndarray, int
	#
	# 	:return: CN curves layer
	# 	:rtype: Numpy ndarray, int
	# 	"""
	#
	# 	hydr_cat = {1:"B", 2:"B",
	# 				3:"C",
	# 				4:"A", 5:"A",
	# 				6:"C",
	# 				7:"D",
	# 				8:"B", 9:"B", 10:"B", 11:"B", 12:"B", 13:"B", 14:"B", 15:"B", 16:"B",
	# 				17:"A",
	# 				18:"B", 19:"B",
	# 				20:"D",
	# 				21:"A",
	# 				22:"B",
	# 				23:"C",
	# 				24:"B", 25:"B", 26:"B", 27:"B", 28:"B", 29:"B", 30:"B",
	# 				31:"A",	32:"A",
	# 				33:"B", 34:"B", 35:"B", 36:"B", 37:"B", 38:"B",
	# 				39:"C",
	# 				40:"B", 41:"B", 42:"B", 43:"B",
	# 				44:"C",	45:"C", 46:"C", 47:"C", 48:"C",
	# 				49:"D",
	# 				50:"C", 51:"C", 52:"C",
	# 				53:"D", 54:"D",
	# 				55:"A",
	# 				56:"B",
	# 				57:"C", 58:"C",
	# 				59:"D",
	# 				60:"B",
	# 				61:"D",
	# 				62:"C",
	# 				63:"D",
	# 				64:"C", 65:"C",
	# 				66:"D", 67:"D", 68:"D", 69:"D", 70:"D", 71:"D", 72:"D", 73:"D", 74:"D",
	# 				75:"C",
	# 				76:"D",
	# 				77:"C",
	# 				78:"C"}
	#
	# 	LU_cat_A = {1:62, 2:, 3:, 4:, 5:, 6:, 7:, 8:, 9:, 10:, 11:,
# 	12:, 13:, 14:, 15:, 16:, 17:, 18:, 19:, 20:, 21:, 22:, 23:, 24:76}
	# 	LU_cat_B = {1:73, 2:, 3:, 4:, 5:, 6:, 7:, 8:, 9:, 10:, 11:,
# 	12:, 13:, 14:, 15:, 16:, 17:, 18:, 19:, 20:, 21:, 22:, 23:, 24:85}
	# 	LU_cat_C = {1:81, 2:, 3:, 4:, 5:, 6:, 7:, 8:, 9:, 10:, 11:,
# 	12:, 13:, 14:, 15:, 16:, 17:, 18:, 19:, 20:, 21:, 22:, 23:, 24:90}
	# 	LU_cat_D = {1:84, 2:, 3:, 4:, 5:, 6:, 7:, 8:, 9:, 10:, 11:,
# 	12:, 13:, 14:, 15:, 16:, 17:, 18:, 19:, 20:, 21:, 22:, 23:, 24:93}
