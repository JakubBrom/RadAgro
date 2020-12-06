#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  Project: RadHydro
#  File: activity_decay.py
#
#  Author: Dr. Jakub Brom
#
#  Copyright (c) 2020. Dr. Jakub Brom, University of South Bohemia in České
#  Budějovice, Faculty of Agriculture.
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
#  Last changes: 28.11.20 1:54
#
#  Begin: 2018/11/14
#
#  Description: Change of activity decay of Cs137 nad Sr90 (Bq/m2)
#  during time.


import numpy as np

class ActivityDecay:
	"""Class of methods dedicated for a calculation of radioactivity
	decay of radionuclides"""

	def __init__(self):
		return

	def calcLambdaConstant(self, half_life):
		"""Calculation of lambda constant for a radionuclide on basis
		of its half life of decay.

		:param half_life: Half life for particular radionuclide (years)

		:return: Lambda constant for a radionuclide :math:`(s^{-1})`
		"""

		# Calculate half life in seconds (from years)
		half_life_s = half_life * 365 * 86400

		# Calculate Lambda constant
		lambda_const = 0.693/half_life_s

		return lambda_const

	def activityDecay(self, A_0, month=1, radionuclide=0):
		"""
		Activity decay (Bq/m2) on basis of relationship:
		A = A_0 * exp(-lambda * t)

		Inputs:
		:param A_0: Activity on the start of the time period (Bq/m2)
		:type A_0: Numpy array (float)
		:param month: Month for which the calculation is done
		:type month: int
		:param radionuclide: Particular radionuclide. Default value
		is 0 for 137Cs. 1 is 90Sr.
		:type radionuclide: int

		Returns:
		:return A: Activity on the end of the time period (Bq/m2)
		:rtype A: Numpy array (float)
		"""

		# Read data
		if A_0 is None:
			raise IOError("Error: Activity layer is not available! "
						  "Calculation has been terminated.")

		# Set half_life
		if radionuclide == 0:		# 137Cs
			half_life = 30.08
		else:
			half_life = 28.79		# 90Sr

		# Calculation of lambda constant
		lbd = self.calcLambdaConstant(half_life)

		# Set number of days in month
		days_in_months = [31,28,31,30,31,30,31,31,30,31,30,31]
		month_days = days_in_months[month-1]

		# Calculation of time duration in sec.
		t_sec = month_days * 86400

		# Calculation of radioactive decay
		A_decay = A_0 * np.exp(-lbd * t_sec)

		return A_decay
