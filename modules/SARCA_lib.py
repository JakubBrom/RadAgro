#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#-----------------------------------------------------------------------
# RadHydro
#
# Module: SARCA_lib.py
#
# Author: Jakub Brom, University of South Bohemia in Ceske Budejovice,
#		  Faculty of Agriculture
#
# Date: 2020/10/31
#
# Description: Calculation of crop growth features and radioactivity
# contamination features
#
# License: Copyright (C) 2020, Jakub Brom, University of South Bohemia
#		   in Ceske Budejovice
#
# Vlastníkem programu RadHydro je Jihočeská univerzita v Českých
# Budějovicích. Všechna práva vyhrazena. Licenční podmínky jsou uvedeny
# v licenčním ujednání (dále jen "smlouva").
# Uživatel instalací nebo použitím programu, jeho verzí nebo aktualizací
# souhlasí s podmínkami smlouvy.
#-----------------------------------------------------------------------

import numpy as np

class SARCALib:

    def __init__(self):
        pass

    def calculateGrowthCoefs(self, dw_max, dw_min=0.1):
        """
        Calculate default values of growth curve parameters - slope
        (m) and intercept (n).

        :param dw_max: Maximal dry mass of particular crop :math:`(
        t.ha^{-1})`
        :param dw_min: Minimal dry mass of particular crop :math:`(
        t.ha^{-1})`. Default value is 0.1 :math:`(
        t.ha^{-1})`.

        :return: Slope of growth curve
        :return: Intercept of growth curve
        """

        intercept = np.log(abs(dw_max/(dw_min-0.001) - 1))
        const = -np.log(abs(dw_max/(dw_max-0.001) - 1))
        slope = intercept + const

        return slope, intercept