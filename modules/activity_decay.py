#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#-----------------------------------------------------------------------
# RadHydro 
#
# Module: activity_decay.py
#
# Author: Jakub Brom, University of South Bohemia in Ceske Budejovice,
#		  Faculty of Agriculture 
#
# Date: 2018/11/14
#
# Description: Change of activity decay of Cs137 (Bq/m2) in time.
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


def activityDecay(A_0, days):
	"""
	Activity decay (Bq/m2) on basis of relationship:
	A = A_0 * exp(-lambda * t)
	
	Inputs:
	:param A_0: Activity on the start of the time period (Bq/m2)
	:type A_0: Numpy array (float)
	:param days: Number of days in time period.
	:type days: float
	
	Returns:
	:return A: Activity on the end of the time period (Bq/m2)
	:rtype A: Numpy array (float)
	"""
	
	if A_0 is None:
		raise IOError("Error: Activity layer is not available! Calculation has been terminated.")
		
	if days is None:
		raise IOError("Error: Number of days for activity decay is not available! Calculation has been terminated.")
	
	t = days * 86400
	lbd = 7.23 * 10**(-10)		# premenova konstanta lambda (s-1)
	
	A = A_0 * np.exp(-lbd * t)
	
	return A
