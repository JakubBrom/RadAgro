#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------
# RadHydro
#
# Module: sowing_procedure.py
# Author: Jakub Brom, University of South Bohemia in Ceske Budejovice,
#		  Faculty of Agriculture
# Begin: 2020/11/04
#
# Description: The model methods are suitable for calculation of
# sowing procedure time series in monthly step. Usable for geodata.
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
import pandas as pd
import numpy as np


class SowingProcTimeSeries:
    """Class SowingProsTimeSeries is a module for calculation of
    sowing procedure time series in monthly step. Calculation is
    based on order of crops in the sowing procedure and their
    agronomy terms (sowing and harvest)"""

    def __int__(self):
        return

    def calcSowingProc(self, crops_table, ID_col_number=0,
                       sowing_col_number=1, harvest_col_number=2):
        """
        Calculation of sowing procedure time series for crops
        included in the crops_table. Output is a list containing IDs
        of crops in sowing procedure.
        The time series starts in January of the first year and
        ending in the December of the last year of the sowing
        procedure. The gaps between crops are highlighted as bare
        soil with ID = 999.

        :param crops_table: Pandas dataframe containing information
        about crops - ID of crop, term of sowing and term of harvest
        in order of the sowing procedure. Terms of sowing and harvest
        are numbered according to months: 1 - January, 2 - February etc.
        :param ID_col_number: crops_table column with IDs index
        :param sowing_col_number: crops_table column with sowing date
        index
        :param harvest_col_number: crops_table column with harvest date
        index

        :return: List containing IDs of crops in sowing procedure.
        The time series starts in January of the first year and
        ending in the December of the last year of the sowing
        procedure.
        """

        # Calculation of the sowing procedure TS
        sow_time_series = []

        # First part of the first year - from January to sowing
        if crops_table.iloc[0, sowing_col_number] < crops_table.iloc[
            len(crops_table) - 1, harvest_col_number]:
            cas_uh = crops_table.iloc[0, sowing_col_number] - 1
        else:
            cas_uh = np.min(crops_table.iloc[:,sowing_col_number] ) - 1

        for i in range(cas_uh):
            sow_time_series.append(999)

        # The following TS 
        for i in range(len(crops_table)):
            if crops_table.iloc[i, harvest_col_number] < crops_table.iloc[i, sowing_col_number]:
                cas_pl = 12 - crops_table.iloc[i, sowing_col_number] + np.min(
                    crops_table.iloc[:,sowing_col_number] )
                for j in range(cas_pl):
                    sow_time_series.append(999)

                cas_pl = crops_table.iloc[i, harvest_col_number] - np.min(
                    crops_table.iloc[:,sowing_col_number] ) + 1
                for j in range(cas_pl):
                    sow_time_series.append(crops_table.iloc[
                                               i, ID_col_number])

            else:
                cas_pl = crops_table.iloc[i, harvest_col_number] - crops_table.iloc[i, sowing_col_number] + 1
                for j in range(cas_pl):
                    sow_time_series.append(crops_table.iloc[
                                               i, ID_col_number])

            try:
                if crops_table.iloc[i + 1, sowing_col_number] < \
                        crops_table.iloc[i, harvest_col_number]:
                    cas_uh = 12 - crops_table.iloc[i,
                                                   harvest_col_number] + crops_table.iloc[i + 1, sowing_col_number] - 1
                else:
                    cas_uh = crops_table.iloc[i + 1,
                                              sowing_col_number] - crops_table.iloc[
                        i, harvest_col_number] - 1
            except Exception:
                break
            for k in range(cas_uh):
                sow_time_series.append(999)  # 999 je pro holou půdu

        # End of TS in the last year - from harvest to December
        if crops_table.iloc[0, sowing_col_number] < crops_table.iloc[
            len(crops_table) - 1, harvest_col_number]:
            cas_uh = 12 - crops_table.iloc[len(crops_table) - 1,
                                           harvest_col_number]
        else:
            cas_uh = 12 - np.min(crops_table.iloc[0, sowing_col_number])

        for i in range(cas_uh):
            sow_time_series.append(999)
            
        return sow_time_series

    def calcMeadows(self, meadows_table, ID_col_number=0, cut_col_number=1):
        """
        Calculation of meadows management (cuts) time series. Output is a
        list containing IDs meadows management (cuts).
        The time series starts in January and ending on the December with
        monthly step.

        :param meadows_table:
        :param ID_col_number:
        :param cut_col_number:
        :return:
        """

        pass

    def predictSowingProc(self, sow_time_series, predict_months=12,
                          start=0):
        """
        Prediction of sowing procedure including agricultural crops and
        cuted meadows.

        :param sow_time_series:
        :param predict_months:
        :param start:
        :return:
        """
        pass
        # TODO: je potřeba rozlišit, jestli se provedlo odstranění biomasy z
        #  ploch v časný fázi a nebo ne. Pokud ano, tak daný rok nebude už
        #  počítaný OP, biomasa ani další sklizeň

    def setHarvestTimeSeries(self):
        # TODO: Vytvoří tabulku s termíny sklizně - asi to bude 1 - sklizeň,
        #  0 - nic
        # TODO: je potřeba rozlišit, jestli se provedlo odstranění biomasy z
        #  ploch v časný fázi a nebo ne. Pokud ano, tak daný rok nebude už
        #  počítaný OP, biomasa ani další sklizeň

        pass

if __name__ == '__main__':
    plodiny_pole = [{'ID': 0, 'name': 'jetel_I', 'kat1': 4, 'kat2': 7},
                    {'ID': 16, 'name': 'jetel_II', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 2, 'name': 'jetel_III', 'kat1': 4,
                     'kat2': 8},
                    {'ID': 6, 'name': 'pšenice', 'kat1': 9, 'kat2': 8},
                    {'ID': 12, 'name': 'ječmen oz.', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 5, 'name': 'brambory', 'kat1': 4, 'kat2': 9},
                    {'ID': 4, 'name': 'ječmen j.', 'kat1': 4,
                     'kat2': 7},
                    {'ID': 9, 'name': 'hrách', 'kat1': 8, 'kat2': 9},
                    {'ID': 1, 'name': 'kukuřice', 'kat1': 4, 'kat2': 9},
                    {'ID': 8, 'name': 'oves', 'kat1': 4, 'kat2': 8},
                    {'ID': 0, 'name': 'jetel_I', 'kat1': 4, 'kat2': 7},
                    {'ID': 1, 'name': 'jetel_II', 'kat1': 9, 'kat2': 7},
                    {'ID': 2, 'name': 'jetel_III', 'kat1': 4,
                     'kat2': 8},
                    {'ID': 6, 'name': 'pšenice', 'kat1': 9, 'kat2': 8},
                    {'ID': 12, 'name': 'ječmen oz.', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 5, 'name': 'brambory', 'kat1': 4, 'kat2': 9},
                    {'ID': 4, 'name': 'ječmen j.', 'kat1': 4,
                     'kat2': 7},
                    {'ID': 9, 'name': 'hrách', 'kat1': 8, 'kat2': 9},
                    {'ID': 1, 'name': 'kukuřice', 'kat1': 4, 'kat2': 9},
                    {'ID': 8, 'name': 'oves', 'kat1': 4, 'kat2': 8},
                    {'ID': 0, 'name': 'jetel_I', 'kat1': 4, 'kat2': 7},
                    {'ID': 16, 'name': 'jetel_II', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 2, 'name': 'jetel_III', 'kat1': 4,
                     'kat2': 8},
                    {'ID': 6, 'name': 'pšenice', 'kat1': 9, 'kat2': 8},
                    {'ID': 12, 'name': 'ječmen oz.', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 5, 'name': 'brambory', 'kat1': 4, 'kat2': 9},
                    {'ID': 4, 'name': 'ječmen j.', 'kat1': 4,
                     'kat2': 7},
                    {'ID': 9, 'name': 'hrách', 'kat1': 8, 'kat2': 9},
                    {'ID': 1, 'name': 'kukuřice', 'kat1': 4, 'kat2': 9},
                    {'ID': 8, 'name': 'oves', 'kat1': 4, 'kat2': 8},
                    {'ID': 0, 'name': 'jetel_I', 'kat1': 4, 'kat2': 7},
                    {'ID': 1, 'name': 'jetel_II', 'kat1': 9, 'kat2': 7},
                    {'ID': 2, 'name': 'jetel_III', 'kat1': 4,
                     'kat2': 8},
                    {'ID': 6, 'name': 'pšenice', 'kat1': 9, 'kat2': 8},
                    {'ID': 12, 'name': 'ječmen oz.', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 5, 'name': 'brambory', 'kat1': 4, 'kat2': 9},
                    {'ID': 4, 'name': 'ječmen j.', 'kat1': 4,
                     'kat2': 7},
                    {'ID': 9, 'name': 'hrách', 'kat1': 8, 'kat2': 9},
                    {'ID': 1, 'name': 'kukuřice', 'kat1': 4, 'kat2': 9},
                    {'ID': 8, 'name': 'oves', 'kat1': 4, 'kat2': 8},
                    {'ID': 0, 'name': 'jetel_I', 'kat1': 4, 'kat2': 7},
                    {'ID': 16, 'name': 'jetel_II', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 2, 'name': 'jetel_III', 'kat1': 4,
                     'kat2': 8},
                    {'ID': 6, 'name': 'pšenice', 'kat1': 9, 'kat2': 8},
                    {'ID': 12, 'name': 'ječmen oz.', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 5, 'name': 'brambory', 'kat1': 4, 'kat2': 9},
                    {'ID': 4, 'name': 'ječmen j.', 'kat1': 4,
                     'kat2': 7},
                    {'ID': 9, 'name': 'hrách', 'kat1': 8, 'kat2': 9},
                    {'ID': 1, 'name': 'kukuřice', 'kat1': 4, 'kat2': 9},
                    {'ID': 8, 'name': 'oves', 'kat1': 4, 'kat2': 8},
                    {'ID': 0, 'name': 'jetel_I', 'kat1': 4, 'kat2': 7},
                    {'ID': 1, 'name': 'jetel_II', 'kat1': 9, 'kat2': 7},
                    {'ID': 2, 'name': 'jetel_III', 'kat1': 4,
                     'kat2': 8},
                    {'ID': 6, 'name': 'pšenice', 'kat1': 9, 'kat2': 8},
                    {'ID': 12, 'name': 'ječmen oz.', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 5, 'name': 'brambory', 'kat1': 4, 'kat2': 9},
                    {'ID': 4, 'name': 'ječmen j.', 'kat1': 4,
                     'kat2': 7},
                    {'ID': 9, 'name': 'hrách', 'kat1': 8, 'kat2': 9},
                    {'ID': 1, 'name': 'kukuřice', 'kat1': 4, 'kat2': 9},
                    {'ID': 8, 'name': 'oves', 'kat1': 4, 'kat2': 8},
                    {'ID': 0, 'name': 'jetel_I', 'kat1': 4, 'kat2': 7},
                    {'ID': 16, 'name': 'jetel_II', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 2, 'name': 'jetel_III', 'kat1': 4,
                     'kat2': 8},
                    {'ID': 6, 'name': 'pšenice', 'kat1': 9, 'kat2': 8},
                    {'ID': 12, 'name': 'ječmen oz.', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 5, 'name': 'brambory', 'kat1': 4, 'kat2': 9},
                    {'ID': 4, 'name': 'ječmen j.', 'kat1': 4,
                     'kat2': 7},
                    {'ID': 9, 'name': 'hrách', 'kat1': 8, 'kat2': 9},
                    {'ID': 1, 'name': 'kukuřice', 'kat1': 4, 'kat2': 9},
                    {'ID': 8, 'name': 'oves', 'kat1': 4, 'kat2': 8},
                    {'ID': 0, 'name': 'jetel_I', 'kat1': 4, 'kat2': 7},
                    {'ID': 1, 'name': 'jetel_II', 'kat1': 9, 'kat2': 7},
                    {'ID': 2, 'name': 'jetel_III', 'kat1': 4,
                     'kat2': 8},
                    {'ID': 6, 'name': 'pšenice', 'kat1': 9, 'kat2': 8},
                    {'ID': 12, 'name': 'ječmen oz.', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 5, 'name': 'brambory', 'kat1': 4, 'kat2': 9},
                    {'ID': 4, 'name': 'ječmen j.', 'kat1': 4,
                     'kat2': 7},
                    {'ID': 9, 'name': 'hrách', 'kat1': 8, 'kat2': 9},
                    {'ID': 1, 'name': 'kukuřice', 'kat1': 4, 'kat2': 9},
                    {'ID': 8, 'name': 'oves', 'kat1': 4, 'kat2': 8},
                    {'ID': 0, 'name': 'jetel_I', 'kat1': 4, 'kat2': 7},
                    {'ID': 16, 'name': 'jetel_II', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 2, 'name': 'jetel_III', 'kat1': 4,
                     'kat2': 8},
                    {'ID': 6, 'name': 'pšenice', 'kat1': 9, 'kat2': 8},
                    {'ID': 12, 'name': 'ječmen oz.', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 5, 'name': 'brambory', 'kat1': 4, 'kat2': 9},
                    {'ID': 4, 'name': 'ječmen j.', 'kat1': 4,
                     'kat2': 7},
                    {'ID': 9, 'name': 'hrách', 'kat1': 8, 'kat2': 9},
                    {'ID': 1, 'name': 'kukuřice', 'kat1': 4, 'kat2': 9},
                    {'ID': 8, 'name': 'oves', 'kat1': 4, 'kat2': 8},
                    {'ID': 0, 'name': 'jetel_I', 'kat1': 4, 'kat2': 7},
                    {'ID': 1, 'name': 'jetel_II', 'kat1': 9, 'kat2': 7},
                    {'ID': 2, 'name': 'jetel_III', 'kat1': 4,
                     'kat2': 8},
                    {'ID': 6, 'name': 'pšenice', 'kat1': 9, 'kat2': 8},
                    {'ID': 12, 'name': 'ječmen oz.', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 5, 'name': 'brambory', 'kat1': 4, 'kat2': 9},
                    {'ID': 4, 'name': 'ječmen j.', 'kat1': 4,
                     'kat2': 7},
                    {'ID': 9, 'name': 'hrách', 'kat1': 8, 'kat2': 9},
                    {'ID': 1, 'name': 'kukuřice', 'kat1': 4, 'kat2': 9},
                    {'ID': 8, 'name': 'oves', 'kat1': 4, 'kat2': 8},
                    {'ID': 0, 'name': 'jetel_I', 'kat1': 4, 'kat2': 7},
                    {'ID': 16, 'name': 'jetel_II', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 2, 'name': 'jetel_III', 'kat1': 4,
                     'kat2': 8},
                    {'ID': 6, 'name': 'pšenice', 'kat1': 9, 'kat2': 8},
                    {'ID': 12, 'name': 'ječmen oz.', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 5, 'name': 'brambory', 'kat1': 4, 'kat2': 9},
                    {'ID': 4, 'name': 'ječmen j.', 'kat1': 4,
                     'kat2': 7},
                    {'ID': 9, 'name': 'hrách', 'kat1': 8, 'kat2': 9},
                    {'ID': 1, 'name': 'kukuřice', 'kat1': 4, 'kat2': 9},
                    {'ID': 8, 'name': 'oves', 'kat1': 4, 'kat2': 8},
                    {'ID': 0, 'name': 'jetel_I', 'kat1': 4, 'kat2': 7},
                    {'ID': 1, 'name': 'jetel_II', 'kat1': 9, 'kat2': 7},
                    {'ID': 2, 'name': 'jetel_III', 'kat1': 4,
                     'kat2': 8},
                    {'ID': 6, 'name': 'pšenice', 'kat1': 9, 'kat2': 8},
                    {'ID': 12, 'name': 'ječmen oz.', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 5, 'name': 'brambory', 'kat1': 4, 'kat2': 9},
                    {'ID': 4, 'name': 'ječmen j.', 'kat1': 4,
                     'kat2': 7},
                    {'ID': 9, 'name': 'hrách', 'kat1': 8, 'kat2': 9},
                    {'ID': 1, 'name': 'kukuřice', 'kat1': 4, 'kat2': 9},
                    {'ID': 8, 'name': 'oves', 'kat1': 4, 'kat2': 8},
                    {'ID': 0, 'name': 'jetel_I', 'kat1': 4, 'kat2': 7},
                    {'ID': 16, 'name': 'jetel_II', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 2, 'name': 'jetel_III', 'kat1': 4,
                     'kat2': 8},
                    {'ID': 6, 'name': 'pšenice', 'kat1': 9, 'kat2': 8},
                    {'ID': 12, 'name': 'ječmen oz.', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 5, 'name': 'brambory', 'kat1': 4, 'kat2': 9},
                    {'ID': 4, 'name': 'ječmen j.', 'kat1': 4,
                     'kat2': 7},
                    {'ID': 9, 'name': 'hrách', 'kat1': 8, 'kat2': 9},
                    {'ID': 1, 'name': 'kukuřice', 'kat1': 4, 'kat2': 9},
                    {'ID': 8, 'name': 'oves', 'kat1': 4, 'kat2': 8},
                    {'ID': 0, 'name': 'jetel_I', 'kat1': 4, 'kat2': 7},
                    {'ID': 1, 'name': 'jetel_II', 'kat1': 9, 'kat2': 7},
                    {'ID': 2, 'name': 'jetel_III', 'kat1': 4,
                     'kat2': 8},
                    {'ID': 6, 'name': 'pšenice', 'kat1': 9, 'kat2': 8},
                    {'ID': 12, 'name': 'ječmen oz.', 'kat1': 9,
                     'kat2': 7},
                    {'ID': 5, 'name': 'brambory', 'kat1': 4, 'kat2': 9},
                    {'ID': 4, 'name': 'ječmen j.', 'kat1': 4,
                     'kat2': 7},
                    {'ID': 9, 'name': 'hrách', 'kat1': 8, 'kat2': 9},
                    {'ID': 1, 'name': 'kukuřice', 'kat1': 4, 'kat2': 9},
                    {'ID': 8, 'name': 'oves', 'kat1': 4, 'kat2': 8}
                    ]
    df_plodiny_pole = pd.DataFrame(plodiny_pole)

    plodiny_op = [{'ID': 0, 'name': 'jetel_I', 'osev': 4, 'skliz': 7},
                  {'ID': 1, 'name': 'jetel_II', 'osev': 9, 'skliz': 7},
                  {'ID': 2, 'name': 'jetel_III', 'osev': 4, 'skliz': 8},
                  {'ID': 6, 'name': 'pšenice', 'osev': 9, 'skliz': 8},
                  {'ID': 12, 'name': 'ječmen oz.', 'osev': 9,
                   'skliz': 7},
                  {'ID': 5, 'name': 'brambory', 'osev': 4, 'skliz': 9},
                  {'ID': 4, 'name': 'ječmen j.', 'osev': 4, 'skliz': 7},
                  {'ID': 9, 'name': 'hrách', 'osev': 8, 'skliz': 9},
                  {'ID': 3, 'name': 'kukuřice', 'osev': 4, 'skliz': 9},
                  {'ID': 8, 'name': 'oves', 'osev': 4, 'skliz': 8}
                  ]

    plodiny = pd.DataFrame(plodiny_op)

    import time

    t1 = time.time()
    sp = SowingProcTimeSeries()

    ts_sp = sp.calcSowingProc(plodiny, 0, 2, 3)
    print(ts_sp)
    t2 = time.time()
    print(t2-t1)
