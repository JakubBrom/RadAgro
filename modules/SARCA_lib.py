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
    """Library for calculation of crops growth parameters and radioactivity
    contamination of crops"""

    def __init__(self):
        return

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

    def timeSeriesConst(self, t_accident, t0, t1):
        """
        Calculation of relative position of the radioactive accident in the
        crop growth time series [0, 1].

        :param t_accident: Date of radioactive accident as number of day in year
        :param t0: Date of sowing crop as number of day in year
        :param t1: Date of harvesting crop as number of day in year

        :return: Relative position of the radioactive accident in the
        crop growth time series
        """

        t0 = np.where(t0 >= t1, 92, t0)

        ts = np.where(t0 >= t1, 0, (t_accident - t0) / (t1 - t0))

        ts[ts > 1.0] = 0.0

        return ts

    def timeScale(self, ts, coef_m, coef_n):
        """
        Calculates scaling value t_scale of crop growth time series.

        :param ts: Relative position of the radioactive accident in the
        crop growth time series
        :param coef_m: Scaling parameter
        :param coef_n: Scaling parameter

        :return: Scaling value of growing time series
        """

        t_scale = coef_m * ts - coef_n

        return t_scale

    def dryMass(self, DW_max, t_accident, t0, t1, coef_m, coef_n):
        """
        Calculation of actual biomass of the particular crop.

        :param DW_max: Maximal dry mass of the crops above ground biomass in
        the growing season :math:`(t.ha^{-1})`
        :param t_accident: Date of radioactive accident as number of day in year
        :param t0: Date of sowing crop as number of day in year
        :param t1: Date of harvesting crop as number of day in year
        :param coef_m: Scaling parameter
        :param coef_n: Scaling parameter

        :return: Dry mass of above ground biomass :math:`(t.ha^{-1})`
        """

        # Time scaling
        ts = self.timeSeriesConst(t_accident, t0, t1)
        t_scale = self.timeScale(ts, coef_m, coef_n)

        # Dry mas of above ground biomass calculation
        dry_mass = np.where(ts != 0.0, DW_max / (1.0 + np.exp(-t_scale)), 0.0)

        return dry_mass

    def leafAreaIndex(self, dw_act, DW_max, LAI_max, R_min, t_accident, t0, t1):
        """
        Calculation of actual LAI of the particular crop.

        :param dw_act: actual dry mass of the crops above ground biomass :math:`(
        t.ha^{-1})`
        :param DW_max: Maximal dry mass of the crops above ground biomass in
        the growing season :math:`(t.ha^{-1})`
        :param LAI_max: Maximal LAI of the crops in the growing season
        :param R_min: Minimal relative wight moisture of the biomass (%)
        :param t_accident: Date of radioactive accident as number of day in year
        :param t0: Date of sowing crop as number of day in year
        :param t1: Date of harvesting crop as number of day in year

        :return: Actual LAI of the crop.
        """

        # Time scaling
        ts = self.timeSeriesConst(t_accident, t0, t1)

        # Dry mas of above ground biomass calculation
        LAI = np.where(ts <= 0.7, LAI_max ** 2 * dw_act / DW_max, (-3.6511 *
                LAI_max + 0.19993 * R_min - 6.66309) * ts ** 2 + (3.9841 *
                LAI_max - 0.14 * R_min + 4.6668) * ts)
        LAI = np.where(LAI > LAI_max, LAI_max, LAI)

        return LAI

    def interceptFactor(self, LAI, precip, DW, k=1.0, S=0.2):
        """
        Interception factor for both dry and wet deposition of
        radionuclides.

        :param LAI: Leaf Area Index (unitless)
        :param k: Constant of radionuclide: I = 0.5, Sr and Ba = 2.0, Cs and \
        another radionuclides = 1.0
        :param precip: Precipitation amount (mm) for period of deposition \
        (ca 24 hours after radiation accident).
        :param DW: Amount of fresh biomass :math:`(t.ha^{-1})`
        :param S: Mean thickness of water film at plant leaves (mm). \
        Default S =	0.2 mm

        :return: Interception Factor (rel.)
        """

        try:
            IF = LAI * k * S * (1.0 - np.exp((-np.log(2.0)) / (3.0 * S) * (
                    precip + 0.0001))) / (precip + 0.0001)
            IF[IF > 1.0] = 1.0
            IF[DW < 0.1] = 0.0
        except ArithmeticError:
            raise ArithmeticError("Interception factor has not been "
                                  "calculated")

        return IF

    def contBiomass(self, depo, IF):
        """
        Radiaoctive contamination of biomass :math:`(Bq.m^{-2})`

        :param depo: Total radioactive deposition :math:`(Bq.m^{-2})`
        :param IF: Interception Factor (rel.)
        :return: Radioactive contamination of biomass :math:`(Bq.m^{-2})`
        """

        try:
            cont_biomass = depo * IF
            cont_biomass = np.where(cont_biomass < 0.0, 0.0, cont_biomass)
        except ArithmeticError:
            raise ArithmeticError("Vegetation biomass radioactive "
                                  "contamination has not been calculated")

        return cont_biomass

    def contSoil(self, depo, IF):
        """
        Radiaoctive contamination of soil :math:`(Bq.m^{-2})`

        :param depo: Total radioactive deposition :math:`(Bq.m^{-2})`
        :param IF: Interception Factor (rel.)
        :return: Radioactive contamination of soil :math:`(Bq.m^{-2})`
        """

        try:
            cont_soil = depo * (1 - IF)
            cont_soil = np.where(cont_soil < 0.0, 0.0, cont_soil)
        except ArithmeticError:
            raise ArithmeticError("Soil radioactive "
                                  "contamination has not been calculated")

        return cont_soil

    def contMass(self, cont_biomass, fresh_biomass):
        """
        Calculation radioactive contamination of fresh vegetation mass \
        :math:`(Bq.kg^{-1})`

        :param cont_biomass: Radioactive deposition on biomass \
        :math:`(Bq.m^{-2})`
        :param fresh_biomass: Amount of fresh biomass of vegetation \
        :math:`(t.ha^{-1})`

        :return: Fresh vegetation mass radioactive contamination \
        :math:`(Bq.kg^{-1})`
        """

        ignore_zero = np.seterr(all="ignore")

        try:
            cont_mass = cont_biomass / (fresh_biomass * 0.1)
            cont_mass[cont_mass < 0.0] = 0.0
        except ArithmeticError:
            raise ArithmeticError("Mass Radioactive "
                                  "contamination of fresh biomass has not "
                                  "been calculated")

        return cont_mass

    def referLevel(self, depo, ref_level1=5000, ref_level2=3000000):
        """
        Mask of radioactive deposition for three reference levels (categories):
        \n

        *0: Low* \n

        *1: Middle* \n

        *2: High*

        \n

        :param depo: Total radioactive deposition :math:`(Bq.m^{-2})`
        :param ref_level1: Lower reference level treshold \
        :math:`(Bq.m^{-2})`. Default value = 5000 :math:`Bq.m^{-2}`
        :param ref_level2: Upper reference level treshold \
        :math:`(Bq.m^{-2})`. Default value = 3000000 :math:`Bq.m^{-2}`
        :return: Mask of radioactive deposition for three reference levels
        """

        try:
            reference_groups = np.where(depo >= ref_level2, 2.0, 1.0)
            reference_groups = np.where(depo >= ref_level1, reference_groups,
                                        0.0)
        except ArithmeticError:
            raise ArithmeticError("Mask for reference levels has not been"
                                  " calculated")

        return reference_groups