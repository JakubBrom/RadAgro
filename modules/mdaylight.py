#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------
# RadHydro 
#
# Module: mdaylight.py
# Author: Jakub Brom, University of South Bohemia in Ceske Budejovice,
#		  Faculty of Agriculture 
# Date: 2018/10/16
#
# Description: The script mdaylight calculates list of monthly mean
#			   daylights according to geographical position
# 
# License: Copyright (C) 2018-2020, Jakub Brom, University of South
# Bohemia
#		   in Ceske Budejovice
# 
# Vlastníkem programu RadHydro je Jihočeská univerzita v Českých 
# Budějovicích. Všechna práva vyhrazena. Licenční podmínky jsou uvedeny
# v licenčním ujednání (dále jen "smlouva").
# Uživatel instalací nebo použitím programu, jeho verzí nebo aktualizací
# souhlasí s podmínkami smlouvy.
#-----------------------------------------------------------------------


# imports
import datetime
import numpy as np
import math as mt


class MonthlyDaylight:
	
	"""Calculates list of monthly mean daylight, timezone and length of
	dailight for particular day according to geographical position."""

	def __init__(self):
		return
		
	def dayLength(self, nday=1, lat=49.1797903):
		
		"""
		Calculation of dalight according to geographic position and day
		number (1-365).
		
		Inputs:
		:param nday: Number of day throughout the year (0-365)
		:type nday: int
		:param lat: Earth latitude (UTM) in decimal degrees
		:type lat: float
		
		Returns
		:return: List of mean monthly daylight (hours, decimal)
		:rtype: list
		"""
				
		# Calculate solar geometry - inputs
		ds = 23.45 * mt.sin(360.0 * (284.0 + float(nday))/365.0 * mt.pi/180.0)		# solar declination (°)	
		ds_rad = mt.radians(ds)                                     			# solar declination (rad.)
		L_rad = mt.radians(lat)                             					# latitude (rad.)
		a = -0.8333																# altitude of the center of solar disc (°)
		a_rad = mt.radians(a)													# altitude of the center of solar disc (rad)
		
		# Calculate day length
		cos_om = (mt.sin(a_rad)-mt.sin(L_rad)*mt.sin(ds_rad))/(mt.cos(L_rad)*mt.cos(ds_rad))
		if cos_om > 1:
			cos_om = 1
		if cos_om < -1:
			cos_om = -1
			
		sunrise = 12 - mt.degrees(mt.acos(cos_om))/15
		sunset = 24 - sunrise
		
		day_length = sunset - sunrise
		
		return day_length
	
	def monthlyDaylights(self, lat=49.1797903):
		
		"""
		Calculation of monthly mean dalight - potential duration of solar 
		radiation
		
		Inputs:
		:param lat: Earth latitude (UTM) in decimal degrees
		:type lat: float
		
		Returns
		:return: List of mean monthly daylight (hours, decimal)
		:rtype: list
		"""
	
		# Variables
		mdays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]	#number of days in month
		dl_nday = []			# length of daylight for each day
		dl_mean_list = []		# mean monthly dalylight 
		
		# Calculation of mean monthly daiyligth (in decimal form)
		j = 1
		for m in range(0, len(mdays)):
			for i in range(j, j + mdays[m]):
				dl = self.dayLength(i, lat)
				dl_nday.append(dl)
	
			j = j + mdays[m]
			dl_mean = np.mean(dl_nday)
			dl_mean_list.append(dl_mean)
			dl_nday = []
		
		return dl_mean_list
