#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#  Project: RadAgro
#  File: waterflow.py
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
#  Last changes: 08.12.20 1:15
#
#  Begin: 2018/11/08
#
#  Description: Module containing methods for calculation of
#  hydrological features of the landscape including water flows
#  calculation (surface and subsurface outflows, potential nd actual
#  evapotranspiration), outflow probability calculation etc. The
#  calculation is designed mostly for monthly data.


# imports
import numpy as np
import math as mt
import warnings
from .mdaylight import MonthlyDaylight


class WaterBalance:
	"""Module for calculation of the hydrological features of the area of
	interest."""

	def __init__(self):
		return

	def airTemperToGrid(self, tm_list, dmt, altitude, adiab=0.65):
		"""
		Calculation of spatial temperature distribution on the altitude (
		DEM). The function provides list (Numpy array) of air
		temperature arrays corresponding to list of measured temperature
		data.
		
		:param tm_list: List of air temperatures measured on a
		meteostation.
		:type tm_list: list
		:param dmt: Digital elevation model.
		:type dmt: Numpy array
		:param altitude: Altitude of temperature measurement.
		:type altitude: float
		:param adiab: Adiabatic change of temeperature with altitude
		per 100 m. Default value is 0.65 °C/100 m.
		:type adiab: float
		
		:return: List of air temperature grids.
		:rtype: Numpy array
		"""
		
		# Convert input temperature list to Numpy array
		tm_list = np.array(tm_list, dtype = float)
		
		# Replace temperature values lower to 1 to 1 --> Calculation of ET
		tm_list = np.where(tm_list < 1.0, 1.0, tm_list)
		
		# Create temperature grids
		tm_grids = [np.array(tm_list[i] + adiab/100 * (altitude -
				dmt), dtype = float) for i in range(0, len(tm_list))]
		# convert to np.array
		tm_grids = np.array(tm_grids, dtype = float)
		
		# Replace temperature values lower to 1 to 1
		tm_grids = np.where(tm_grids <= 1.0, 1.0, tm_grids)
		
		return tm_grids

	def evapoPot(self, tm_grids, lat = 49.1797903):
		"""
		Potential monthly ET According to Thornthwaite 1948. Script
		calculates ETpot for the whole year - for each month. 
		
		:param tm_grids: List of monthly mean air temperatures during
		the year (degree of Celsius) - temperature normals
		:type tm_grids: list
		:param lat: Earth latitude (UTM) in decimal degrees
		:type lat: float
		
		:return ET_pot: Potential monthly evapotranspiration
		according to Thornthwaite (1984), mm. List of monthly values
		for the year.
		:rtype: Numpy array
		"""
		
		# inputs
		n_days = np.array((31,28,31,30,31,30,31,31,30,31,30,31),
						  dtype = np.float) # length of month
		md = MonthlyDaylight()
		# list of mean monthly daylights (dec. hour)
		dl = md.monthlyDaylights(lat)
		dl = np.array(dl, dtype = float)
		
		# temperature grids manipulation
		tm_grids = np.array(tm_grids, dtype = np.float)
		tm_grids = np.where(tm_grids <= 0, 1.0, tm_grids) 
		
		# calculate constats:
		ij = (tm_grids/5)**1.514
		I = sum(ij)
		a = (0.0675 * I**3 - 7.71 * I**2 + 1792 * I + 47239) * 10**(-5)
	
		# calculate mean potential ET grids
		ETpot_list = [16 * dl[i]/12 * n_days[i]/30 * (10 * tm_grids[
			i]/I)**a for i in range(0, len(tm_grids))]
		
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
			warnings.warn("Warning: Evapotranspiration data contains "
						  "NANs.", stacklevel=3)

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
	
	def runoffSeparCN(self, acc_precip, ET, ETp, I, CN=65,  a=0.005,
					  b=0.005, c=0.5):
		"""
		The script separates precipitation amount (accumulated) into
		surface runoff, water retention and evapotranspiration for
		monthly precipitation data. The method is based on the modified
		CN curve method.
		
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

		:return: Amount of monthly surface runoff (mm) corrected on ET
		:rtype: float
		:return: Amount of retention of water in the soil or
		subsurface runoff (mm) corrected on ET
		:rtype: float
		:return: Monthly amount of actual evapotranspiration from the
		surface (mm)
		:rtype: float
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
		
		:param win_dmt: 3x3 matrix of elevation model.
		:type win_dmt: numpy array
		:param xsize: Size of pixel in x axis (m)
		:type xsize: float
		:param ysize: Size of pixel in y axis (m)
		:type ysize: float

		:return: 3 x 3 matrix of probability of water runoff
		:rtype: Numpy array
		"""
		
		# Input data processing
		x,y = win_dmt.shape
		if x != 3 or y != 3:
			raise IOError("Error: Probability of water flow direction"
						  "can not be calculated! Calculation has "
						  "been terminated.")
		
		# find difference between lower cells and center cell
			# spocte rozdíl mezi centralni bunkou a hodnotami mensimi
			# nez centralni bunka. Ostatni jsou 0 vcetne centralni
		diff = np.where(win_dmt < win_dmt[1,1], win_dmt[1,
						1] - win_dmt, 0)
		
		# reseni plochych mist bez sklonu - predpokladem je vsesmerny
		# odtok
		if diff.sum() == 0:
			diff = np.ones((3,3), dtype = float)
			diff[1,1] = 1
		else:
			# vypocet pravdepodobnosti odtoku do jednotlivych pixelu
			# na zaklade geometrie (uhel sklonu) ==> uhel(alfa)/90
			# ==> pravdepodobnost se meni linearne se sklonem
			diff[0,1] = 2 * mt.atan(diff[0,1]/ysize)/mt.pi									#N
			diff[1,2] = 2 * mt.atan(diff[1,2]/xsize)/mt.pi									#E
			diff[2,1] = 2 * mt.atan(diff[2,1]/ysize)/mt.pi									#S
			diff[1,0] = 2 * mt.atan(diff[1,0]/xsize)/mt.pi									#W
			diff[0,2] = 2 * mt.atan(diff[0,2]/mt.sqrt(xsize**2 + ysize**2))/mt.pi			#NE
			diff[2,2] = 2 * mt.atan(diff[2,2]/mt.sqrt(xsize**2 + ysize**2))/mt.pi			#SE
			diff[2,0] = 2 * mt.atan(diff[2,0]/mt.sqrt(xsize**2 + ysize**2))/mt.pi			#SW
			diff[0,0] = 2 * mt.atan(diff[0,0]/mt.sqrt(xsize**2 + ysize**2))/mt.pi			#NW
		
		# pravdepodobnost odtoku do jednotlivych smeru. Suma
		# pravdepodobnosti = 1.
		probab = diff/diff.sum()
		
		return probab

	def waterFlows(self, dmt, precip, CN, LAI, ETp, xsize=1.0,
				   ysize=1.0, a=0.005, b=0.005, c=0.5, d=0.1, e=0.2):
		"""
		Calculation of water flows (surface, subsurface and
		evapotranspiration) in the area of interest. Calculation is
		designed for monthly data. The area for calculation is
		defined by raster of digital elevation model. Calculation of
		water flows are based on CN curves approach and actual
		evapotranspiration is calculated on basis of Thornthwaith
		and Ol'decop.

		:param dmt: Digital elevation model of the surface (m).
		:type dmt: Numpy array
		:param precip: Grid (Numpy array) of precipitation amount
		for particular month (mm) corresponding to dmt
		:type precip: Numpy array
		:param CN: Grid (Numpy array) of CN curves
		:type CN: Numpy array
		:param LAI: Leaf area index
		:type LAI: Numpy array
		:param ETp: Potential evapotranspiration (mm/month)
		:type ETp: Numpy array
		:param xsize: Size of pixel in x axis (m)
		:type xsize: float
		:param ysize: Size of pixel in y axis (m)
		:type ysize: float
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

		:return: Surface outflow of water (mm/month)
		:rtype: Numpy array
		:return: Subsurface outflow of water (mm/month)
		:rtype: Numpy array
		:return: Actual evapotranspiration (mm/month)
		:rtype: Numpy array
		"""

		# dividing by zero is ignored
		ignore_zero = np.seterr(all = "ignore")
	
		# Handling input grids
		## DEM
		if dmt is None:
			raise IOError("Error: Elevation data are not available! "
						  "Calculation has been terminated.")
		dmt = np.array(dmt, dtype = float)
		## Precipitation
		if precip is None:
			raise IOError("Error: Precipitation data are not "
						  "available! Calculation has been terminated.")
		precip = np.array(precip, dtype = float)
		##CN curves
		if CN is None:
			raise IOError("Error: CN curves layer is not available! "
						  "Calculation has been terminated.")
		CN = np.array(CN, dtype = float)
		##LAI - leaf area index
		if LAI is None:
			raise IOError("Error: Leaf area index data are not "
						  "available! Calculation has been terminated.")
		LAI = np.array(LAI, dtype = float)
		##ETp - potential ET
		if ETp is None:
			raise IOError("Error: Potential evapotranspiration data "
						  "are not available! Calculation has been "
						  "terminated.")
		ETp = np.array(ETp, dtype = float)

		## Fill NANs by mean of neighbour values in raster (by rows)
		if np.isnan(np.sum(dmt)) == True:
			mask = np.isnan(dmt)
			dmt[mask] = np.interp(np.flatnonzero(mask),
								  np.flatnonzero(~mask), dmt[~mask])
			warnings.warn("Warning: The elevation data contains NANs. "
						  "NANs has been filled.", stacklevel=3)
	
		# Preparation DEM data
		# prevedeni na radu podle sloupcu (Fortran styl) --> je to
		# asi jedno. Hodnoty jsou orizle o okrajove bunky.
		dmt_flat = dmt[1:-1,1:-1].flatten("F")
		# usporadani hodnot podle vyskopisu --> od nejmensi po
		# nejvetsi hodnotu. Algoritmus vraci indexy pozice hodnot v
		# puvodnim souboru.
		index_dmt = np.argsort(dmt_flat,axis=0,kind='mergesort')

		# Preparation of intercept
		interc = self.interceptWater(precip, LAI, d, e)
		
		# Preparation of accumulation layers
		# startovni vrstva akumulace povrchoveho odtoku
		surf_acc = np.zeros_like(dmt).astype(float)
		# startovni vrstva akumulace podpovrchoveho odtoku
		subsurf_acc = np.zeros_like(dmt).astype(float)
		# startovni vrstva aktualniho vyparu
		ET_acc = np.zeros_like(dmt).astype(float)

		nrows=dmt.shape[0]-2	# pocet sloupcu a radku bez okrajovych
		
		# Calculation of precip. water accumulation
		# postupuje podle indexu v poradi od nejvetsi do nejmensi
		# hodnoty
		for i in index_dmt[::-1]:
			
			#define position of calculation window
			y=int(i%nrows)		# vrati zbytek po deleni
			x=int(i/nrows)		# 

			# create 3x3 windows for calculation
			# vyreze matice 3x3 z dmt v poradi podle index_dmt
			win_dmt = dmt[y:y+3,x:x+3]
			
			# calculate probability of water flow
			probab = self.flowProbab(win_dmt, xsize, ysize)
			
			# Surface and subsurface runoff, ETa
			# celkovy uhrn vody, ktera muze nekam odtekat
			total_water = surf_acc[y+1,x+1] + precip[y+1,x+1]
			# evapotranspiration
			ET = self.evapoActual(ETp[y+1,x+1], total_water)
						
			# Flows after correction
			Rcor, Scor, ETa = self.runoffSeparCN(total_water, ET,
							ETp[y+1,x+1], interc[y+1,x+1], CN[y+1,
							x+1], a=a, b=b, c=c)

			# Calculation proportions of water flows from precipitation
			surfrun = (precip[y+1,x+1] - ETa) * (Rcor/(total_water - ETa))
			subrun = (precip[y+1,x+1] - ETa) * (Scor/(total_water - ETa))
			if surfrun <= 0:
				surfrun = 0
			if subrun <= 0:
				subrun = 0

			#proportionally distribute
			# akumulace povrchoveho odtoku
			surf_acc[y:y+3,x:x+3] += probab * (surf_acc[y+1,x+1] + surfrun)
			# akumulace podpovrchoveho odtoku
			subsurf_acc[y:y+3,x:x+3] += probab * (subsurf_acc[y+1, x+1] + subrun)
			ET_acc[y+1, x+1] += ETa						# ETa
			
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
		The method calculation procedure was inspired by
		Multipath-Flow-Accumulation developed by Alex Stum:
		https://github.com/StumWhere/Multipath-Flow-Accumulation.git
		
		:param dmt: Digital elevation model of the surface (m).
		:type dmt: numpy.ndarray
		:param xsize: Size of pixel in x axis (m)
		:type xsize: float
		:param ysize: Size of pixel in y axis (m)
		:type ysize: float
		:param rs: Surface resistance for surface runoff of water
		scaled to interval <0; 1>, where 0 is no resistance and 1 is
		100% resistance (no flow). Scaled Mannings n should be used.
		Default is None (zero resistance is used).
		:type rs: numpy.ndarray
		
		:return: Flow accumulation grid.
		:rtype: numpy.ndarray
		"""
	
		# dividing by zero is ignored
		ignore_zero = np.seterr(all = "ignore")
	
		# Handling dmt data
		if dmt is None:
			raise IOError("Error: Elevation data are not available! "
						  "Calculation has been terminated.")
		
		## Fill NANs by mean of neighbour values in raster (by rows)
		if np.isnan(np.sum(dmt)) == True:
			mask = np.isnan(dmt)
			dmt[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(
				~mask), dmt[~mask])
			warnings.warn("Warning: The elevation data contains NANs."
						  "No data has been filled.", stacklevel=3)
	
		# Handling surface resistance - zero resistance is default
		if rs is None:
			rs = np.zeros_like(dmt).astype(float)
		
		## Fill NANs by 0
		if np.isnan(np.sum(rs)) == True:
			rs = np.nan_to_num(rs)
			warnings.warn("Warning: The surface resistance data "
						  "contains NANs. No data has been filled.",
						  stacklevel=3)
		
		## Trimm values of rs to interval <0,1> 
		if np.max(rs) > 1 or np.min(rs) < 0:
			warnings.warn("Warning: The surface resistance data "
						  "contains values out of required "
						  "interval! Values out of interval <0; 1> "
						  "were replaced either by 1 if the values "
						  "are bigger than 1 or by 0 if the values "
						  "are lower than 0", stacklevel=3)
			rs = np.where(rs > 1, 1, rs)
			rs = np.where(rs < 0, 0, rs)
		
		## All values of rs are bigger than 1
		if np.mean(rs) >= 1:
			raise ValueError("Error: Flow accumulation can not be "
							 "calculated! Surface resistance does"
							 "not allow runoff.")
		
		## Control of spatial extent
		if rs.shape[0] != dmt.shape[0] or rs.shape[1] != dmt.shape[1]:
			raise ValueError("Error: Flow accumulation can not be "
							 "calculated! Spatial extent of digital "
							 "elevation model and surface resistance "
							 "layer does not match.")
		
		# Preparation DEM data
		# prevedeni na radu podle sloupcu (Fortran styl). Hodnoty
		# jsou orizle o okrajove bunky.
		dmt_flat = dmt[1:-1,1:-1].flatten("F")
		# usporadani hodnot podle vyskopisu --> od nejmensi po nejvetsi
		# hodnotu. Algoritmus vraci indexy pozice hodnot v puvodnim
		# souboru.
		index_dmt = np.argsort(dmt_flat,axis=0,kind='mergesort')
		# startovni vrstva akumulace odtoku --> predpoklada
		# jednickovy odtok
		accum = np.ones_like(dmt).astype(float) #* precip
		# pocet sloupcu a radku bez okrajovych
		nrows = dmt.shape[0]-2
		
		# Calculation of precip. water accumulation
		# postupuje podle indexu v poradi od nejvetsi do nejmensi hodnoty
		for i in index_dmt[::-1]:
			
			# Define position of calculation window
			y = int(i%nrows)		# vrati zbytek po deleni
			x = int(i/nrows)		#

			# create 3x3 windows for calculation
			# vyreze matice 3x3 z dmt v poradi podle index_dmt
			win_dmt = dmt[y:y+3,x:x+3]
			# vyrez matice 3x3 z odporu povrchu pro odtok (něco jako
			# Manning: hodnoty v intervalu <0, 1>, kde 0 => zadny
			# odpor, 1 => blokovany odtok)
			win_rs = rs[y:y+3,x:x+3]

			# Find difference between lower cells and center cell
			# spocte rozdíl mezi centralni bunkou a hodnotami mensimi
			# nez centralni bunka. Ostatni jsou 0 vcetne centralni
			diff = np.where(win_dmt < win_dmt[1,1], win_dmt[1,
					1] - win_dmt, 0)

			# reseni plochych mist bez sklonu - predpokladem je
			# vsesmerny odtok
			if diff.sum() == 0:
				diff = np.ones((3,3), dtype = float)
				diff[1,1] = 0
			else:
				# vypocet pravdepodobnosti odtoku do jednotlivych
				# pixelu na zaklade geometrie (uhel sklonu) ==> uhel(
				# alfa)/90 ==> pravdepodobnost se meni linearne se
				# sklonem
				diff[0,1] = 2 * mt.atan(diff[0,1]/ysize)/mt.pi									#N
				diff[1,2] = 2 * mt.atan(diff[1,2]/xsize)/mt.pi									#E
				diff[2,1] = 2 * mt.atan(diff[2,1]/ysize)/mt.pi									#S
				diff[1,0] = 2 * mt.atan(diff[1,0]/xsize)/mt.pi									#W
				diff[0,2] = 2 * mt.atan(diff[0,2]/mt.sqrt(xsize**2 + ysize**2))/mt.pi			#NE
				diff[2,2] = 2 * mt.atan(diff[2,2]/mt.sqrt(xsize**2 + ysize**2))/mt.pi			#SE
				diff[2,0] = 2 * mt.atan(diff[2,0]/mt.sqrt(xsize**2 + ysize**2))/mt.pi			#SW
				diff[0,0] = 2 * mt.atan(diff[0,0]/mt.sqrt(xsize**2 + ysize**2))/mt.pi			#NW
			
			# Application of surface resistance on probability of
			# runoff accumulation
			prob_pix = diff * (1 - win_rs)
			
			# pravdepodobnost odtoku do jednotlivych smeru. Suma
			# pravdepodobnosti = 1.
			probab = prob_pix/prob_pix.sum()
			
			# proportionally distribute
			# pripocte ke stavajici matici accum pravdepodobnosti
			# odtoku. Pravdepodobnost dtoku se nasobi uhrnem srazek (
			# pro centralni bunku)
			# accum[y+1,x+1] je suma srazek z predchoziho vypoctu
			accum[y:y+3,x:x+3] += probab * accum[y+1,x+1]

		#accum = np.nan_to_num(accum)
		acc_mask = np.isnan(accum)
		accum[acc_mask] = 1.0
	
		return accum
