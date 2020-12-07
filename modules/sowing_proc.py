#  Project: RadHydro
#  File: sowing_proc.py
#
#  Author: Dr. Jakub Brom
#
#  Copyright (c) 2020. Dr. Jakub Brom, University of South Bohemia
#  in České Budějovice, Faculty of Agriculture.
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
#  Last changes: 25.11.20 23:50
#
#  Begin: 2020/11/04
#
#  Description: The model methods are suitable for calculation of
#  sowing procedure time series in monthly step. Usable for geodata.


import pandas as pd
import numpy as np
from .SARCA_lib import SARCALib
sl = SARCALib()


class SowingProcTimeSeries:
    """Class SowingProsTimeSeries is a module for calculation of
    sowing procedure (crop rotation) time series in monthly step.
    Calculation is based on order of crops in the sowing procedure
    and their agronomy terms (sowing and harvest)"""

    def __int__(self):
        return

    def calcSowingProc(self, crops_table, ID_col_number=0,
                       sowing_col_number=1, harvest_col_number=2):
        """
        Calculation of sowing procedure time series for crops or for
        mowed meadows. Calculates are tables for crops identifiers,
        and table with difference of days between sowing and harvest.
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
        :return: List containing sowing days of crops (approximate
        values taken from number of months).
        :return: List containing harvesting days of crops (approximate
        values taken from number of months).
        """

        # Check the consistency of data - if the month of harvesting
        # is equal to following month of sowing, the month of sowing
        # is increased by 1
        for i in range(len(crops_table)):
            try:
                if crops_table.iloc[i+1, sowing_col_number] == \
                        crops_table.iloc[i, harvest_col_number]:
                    crops_table.iloc[i+1,sowing_col_number] = \
                        crops_table.iloc[i+1,sowing_col_number] + 1
            except Exception:
                break

        # Calculation of the sowing procedure TS
        crops_ts = []
        t0_ts = []
        t1_ts = []

        # First part of the first year - from January to sowing
        if crops_table.iloc[0, sowing_col_number] < crops_table.iloc[
            len(crops_table) - 1, harvest_col_number]:
            cas_uh = crops_table.iloc[0, sowing_col_number] - 1
        else:
            cas_uh = np.min(crops_table.iloc[:,sowing_col_number]) - 1

        for i in range(cas_uh):
            crops_ts.append(-999)
            t0_ts.append(0)
            t1_ts.append(0)

        # The following TS
        for i in range(len(crops_table)):
            if crops_table.iloc[i, harvest_col_number] < \
                    crops_table.iloc[i, sowing_col_number]:
                cas_pl = 12 - crops_table.iloc[i, sowing_col_number] + np.min(
                    crops_table.iloc[:,sowing_col_number])
                for j in range(cas_pl):
                    crops_ts.append(-999)
                    t0_ts.append(0)
                    t1_ts.append(0)

                cas_pl = crops_table.iloc[i, harvest_col_number] - np.min(
                    crops_table.iloc[:,sowing_col_number]) + 1
                for j in range(cas_pl):
                    crops_ts.append(crops_table.iloc[
                                               i, ID_col_number])
                    t0_ts.append(np.min(crops_table.iloc[:,
                                 sowing_col_number]) - 1)
                    t1_ts.append(crops_table.iloc[i,
                                                  harvest_col_number])

            else:
                cas_pl = crops_table.iloc[i, harvest_col_number] - crops_table.iloc[i, sowing_col_number] + 1
                for j in range(cas_pl):
                    crops_ts.append(crops_table.iloc[
                                               i, ID_col_number])
                    t0_ts.append(crops_table.iloc[i,
                                    sowing_col_number] - 1)
                    t1_ts.append(crops_table.iloc[i,
                                                  harvest_col_number])

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
                crops_ts.append(-999)  # 999 je pro holou půdu
                t0_ts.append(0)
                t1_ts.append(0)

        # End of TS in the last year - from harvest to December
        if crops_table.iloc[0, sowing_col_number] < crops_table.iloc[
            len(crops_table) - 1, harvest_col_number]:
            cas_uh = 12 - crops_table.iloc[len(crops_table) - 1,
                                           harvest_col_number]
        else:
            cas_uh = 12 - np.min(crops_table.iloc[0, sowing_col_number])

        for i in range(cas_uh):
            crops_ts.append(-999)
            t0_ts.append(0)
            t1_ts.append(0)

        t0_ts_day = [t0_ts[i] * 30 for i in
                              range(len(t0_ts))]
        t1_ts_day = [t1_ts[i] * 30 for i in
                     range(len(t1_ts))]

        return crops_ts, t0_ts_day, t1_ts_day

    def predictCropsRotation(self, crops_table, ID_col_number=0,
                             sowing_col_number=1, harvest_col_number=2,
                             predict_months=12, start_month=1,
                             early_stage_mng=True):
        """
        Prediction of sowing procedure including agricultural crops or
        mowed meadows. List of crops signatures in TS. -999 is bare
        soil.

        :param crops_table: Pandas dataframe containing information
        about crops - ID of crop, term of sowing and term of harvest
        in order of the sowing procedure. Terms of sowing and harvest
        are numbered according to months: 1 - January, 2 - February etc.
        :param ID_col_number: crops_table column with IDs index
        :param sowing_col_number: crops_table column with sowing date
        index
        :param harvest_col_number: crops_table column with harvest date
        index
        :param predict_months: Number of months for prediction
        :param start_month: Month of prediction start - month of
        radiation accident. [1-12]
        :param early_stage_mng: The removing of biomass in early
        stage of radioactive contamination has been done or not. I
        the first case, the first year of the prediction is taken as
        bare soil.

        :return: Basic dataframe (Pandas) for all crops and meadows for
        the whole TS of the prediction. Data are ordered according to
        sowing procedure following the particular crops in the crops
        rotation.
        """

        # Calculate time series for crops rotation
        crops_ts = self.calcSowingProc(crops_table,
                                              ID_col_number,
                                              sowing_col_number,
                                              harvest_col_number)[0]

        # Crops table ID name
        crops_ID_name = crops_table.columns[ID_col_number]

        # Increasing the TS of the crops rotation to length of
        # prediction time
        no_iter = predict_months // len(crops_ts) + 2
        crops_ts_init = []
        for i in range(no_iter):
            crops_ts_init.extend(crops_ts)

        # Create names of months - M1 is the first month of prediction,
        # M2 second etc.
        col_names = [("M{no}").format(no=str(i + 1)) for i in range(
            predict_months)]
        col_names.insert(0, crops_ID_name)

        # Create a new list of TSs for particular crops in the crop
        # rotation procedure
        # Initial list
        all_op_list = []

        # Loop for arranging TSs for particular crops and cut them to
        # the prediction length
        for i in range(len(crops_table)):
            # Looking for a start in the TS for particular crop
            crops_ts_start = crops_ts_init.index(
                crops_table[crops_ID_name][i]) - \
                             crops_ts_init.index(
                crops_table[crops_ID_name][i]) % 12 + \
                             start_month - 1

            # Create
            crops_list = crops_ts_init[crops_ts_start:crops_ts_start
                                                      + predict_months]

            crops_list.insert(0, crops_table[crops_ID_name][i])
            pl_dict = {col_names[i]: crops_list[i] for i in
                       range(len(crops_list))}
            all_op_list.append(pl_dict)

        df_crops_ts = pd.DataFrame(all_op_list)

        # If the biomass is removed in the early stage the rest
        # of the year is bare soil only
        if early_stage_mng is True:
            no_to_year_end = 12 - start_month
            df_crops_ts.loc[0:len(df_crops_ts), 1:(no_to_year_end+1)]\
                = -999

        return df_crops_ts

    def predictDryMass(self, crops_table, params_table, ID_col_number=0,
                       sowing_col_number=1, harvest_col_number=2,
                       predict_months=12, start_month=1,
                       early_stage_mng=True):
        """
        Prediction of dry mass of agricultural crops or
        mowed meadows.

        :param crops_table: Pandas dataframe containing information
        about crops - ID of crop, term of sowing and term of harvest
        in order of the sowing procedure. Terms of sowing and harvest
        are numbered according to months: 1 - January, 2 - February etc.
        :param params_table: Pandas dataframe with parameters for
        calculation of dry mass of crops and meadows.
        :param ID_col_number: crops_table column with IDs index
        :param sowing_col_number: crops_table column with sowing date
        index
        :param harvest_col_number: crops_table column with harvest date
        index
        :param predict_months: Number of months for prediction
        :param start_month: Month of prediction start = month of
        radiation accident. [1-12]
        :param early_stage_mng: The removing of biomass in early
        stage of radioactive contamination has been done or not. I
        the first case, the first year of the prediction is taken as
        bare soil.

        :return: Dataframe of all crops and meadows dry mass for
        the whole TS of the prediction. Data are ordered according to
        sowing procedure following the particular crops in the crops
        rotation.
        """

        # Calculate time series for crops rotation, t0 and t1
        crops_ts, t0_ts, t1_ts = self.calcSowingProc(crops_table,
                                              ID_col_number,
                                              sowing_col_number,
                                              harvest_col_number)

        # Change lists to Numpy arrays and replacing values > 99 to
        # 20 which corresponds to meadows
        crops_ts_arr = np.array(crops_ts)
        crops_ts_arr[crops_ts_arr > 99] = 20
        t0_ts = np.array(t0_ts)
        t1_ts = np.array(t1_ts)
        t_ts = []
        for i in range(len(crops_ts)//12):
            seq = list(range(1,13))
            t_ts.extend(seq)

        # Changing months to days
        t_ts = np.array(t_ts) * 30

        # Get name of ID column in params table
        id_crops_par = params_table.columns[0]

        # Merging crops_rotation and crops parameters tables
        df_dw_ts = pd.DataFrame({id_crops_par:crops_ts_arr})
        df_crops_merge = pd.merge(df_dw_ts, params_table,
                                  how="left", on=id_crops_par)

        # Extract max. dry mass and coefficients - tho position of
        # columns in source df is fix
        dw_max = np.array(df_crops_merge.iloc[:,3])
        coef_m = np.array(df_crops_merge.iloc[:,7])
        coef_n = np.array(df_crops_merge.iloc[:,8])

        # Calculate DW for particular months and create new list of DWs
        dw_list = sl.dryMass(dw_max, t_ts, t0_ts, t1_ts, coef_m,
                             coef_n)

        # Crops table ID name
        crops_ID_name = crops_table.columns[ID_col_number]

        # Increasing the TS of the crops rotation to length of
        # prediction time
        no_iter = predict_months // len(dw_list) + 2
        dw_ts_init = []
        crops_ts_init = []
        for i in range(no_iter):
            dw_ts_init.extend(dw_list)
            crops_ts_init.extend(crops_ts)

        # Create names of months - M1 is the first month of prediction,
        # M2 second etc.
        col_names = [("M{no}").format(no=str(i + 1)) for i in range(
            predict_months)]
        col_names.insert(0, crops_ID_name)

        # Create a new list of TSs for particular crops dw in the crop
        # rotation procedure
        # Initial list
        all_dw_list = []

        # Loop for arranging TSs for particular crops dw and cut them to
        # the prediction length
        for i in range(len(crops_table)):
            # Looking for a start in the TS for particular crop
            crops_ts_start = crops_ts_init.index(
                crops_table[crops_ID_name][i]) - \
                             crops_ts_init.index(
                crops_table[crops_ID_name][i]) % 12 + \
                             start_month - 1

            # Create
            dw_ts = dw_ts_init[crops_ts_start:crops_ts_start
                                                      + predict_months]
            dw_ts.insert(0, crops_table[crops_ID_name][i])
            dw_dict = {col_names[i]: dw_ts[i] for i in
                       range(len(dw_ts))}

            all_dw_list.append(dw_dict)

        df_dw_ts = pd.DataFrame(all_dw_list)

        # If the biomass is removed in the early stage the rest
        # of the year is bare soil only
        if early_stage_mng is True:
            no_to_year_end = 12 - start_month
            df_dw_ts.loc[0:len(df_dw_ts), 1:(no_to_year_end+1)] = 0

        return df_dw_ts

    def predictHarvest(self, crops_table, ID_col_number=0,
                             sowing_col_number=1, harvest_col_number=2,
                             predict_months=12, start_month=1,
                             early_stage_mng=True):
        """
        Prediction of harvest time for agricultural crops or
        mowed meadows.

        :param crops_table: Pandas dataframe containing information
        about crops - ID of crop, term of sowing and term of harvest
        in order of the sowing procedure. Terms of sowing and harvest
        are numbered according to months: 1 - January, 2 - February etc.
        :param ID_col_number: crops_table column with IDs index
        :param sowing_col_number: crops_table column with sowing date
        index
        :param harvest_col_number: crops_table column with harvest date
        index
        :param predict_months: Number of months for prediction
        :param start_month: Month of prediction start - month of
        radiation accident. [1-12]
        :param early_stage_mng: The removing of biomass in early
        stage of radioactive contamination has been done or not. I
        the first case, the first year of the prediction is taken as
        bare soil.

        :return: Basic dataframe (Pandas) for all crops and meadows for
        the whole TS of the prediction. Data are ordered according to
        sowing procedure following the particular crops in the crops
        rotation.
        """

        # Calculate time series for crops rotation
        crops_ts, sow_ts, harv_ts = self.calcSowingProc(crops_table,
                                              ID_col_number,
                                              sowing_col_number,
                                              harvest_col_number)

        # Crops table ID name
        crops_ID_name = crops_table.columns[ID_col_number]

        # Create time series for crops harvesting time - 0 is no
        # activity, 1 is harvest

        harvest_list = []

        for i in range(len(harv_ts) - 1):
            if harv_ts[i] == harv_ts[i + 1]:
                harvest_list.append(0)
            else:
                harvest_list.append(1)
        harvest_list.append(0)

        crops_ts = np.array(crops_ts)
        harvest_list = np.where(crops_ts == -999, 0, harvest_list)

        # Increasing the TS of the crops rotation to length of
        # prediction time
        no_iter = predict_months // len(crops_ts) + 2
        harvest_ts_init = []
        crops_ts_init = []
        for i in range(no_iter):
            harvest_ts_init.extend(harvest_list)
            crops_ts_init.extend(crops_ts)

        # Create names of months - M1 is the first month of prediction,
        # M2 second etc.
        col_names = [("M{no}").format(no=str(i + 1)) for i in range(
            predict_months)]
        col_names.insert(0, crops_ID_name)

        # Create a new list of TSs for particular crops in the crop
        # rotation procedure
        # Initial list
        all_hv_list = []

        # Loop for arranging TSs for particular crops and cut them to
        # the prediction length
        for i in range(len(crops_table)):
            # Looking for a start in the TS for particular crop
            crops_ts_start = crops_ts_init.index(
                crops_table[crops_ID_name][i]) - \
                             crops_ts_init.index(
                crops_table[crops_ID_name][i]) % 12 + \
                             start_month - 1

            # Create
            harvest_ts = harvest_ts_init[crops_ts_start:crops_ts_start
                                                      + predict_months]

            harvest_ts.insert(0, crops_table[crops_ID_name][i])
            hv_dict = {col_names[i]: harvest_ts[i] for i in
                       range(len(harvest_ts))}

            all_hv_list.append(hv_dict)

        df_harvest_ts = pd.DataFrame(all_hv_list)

        # If the biomass is removed in the early stage the rest
        # of the year is bare soil only
        if early_stage_mng is True:
            no_to_year_end = 12 - start_month
            df_harvest_ts.loc[0:len(df_harvest_ts), 1:(no_to_year_end+1)]\
                = 0

        return df_harvest_ts


if __name__ == '__main__':
    # Testing
    import time
    from matplotlib import pyplot as plt

    # Table with all data - i.e. vector polygons features
    IDs = [0, 16, 2, 6, 12, 5, 4, 9, 1, 8, 0, 1, 2, 6, 12, 5, 4, 9,
           1, 8, 0, 16, 2, 6, 12, 5, 4, 9, 1, 8, 0]
    names = ['jetel_I', 'jetel_II', 'jetel_III', 'pšenice', 'ječmen '
             'oz.', 'brambory', 'ječmen j.', 'hrách', 'kukuřice',
             'oves', 'jetel_I', 'jetel_II', 'jetel_III', 'pšenice',
             'ječmen oz.', 'brambory', 'ječmen j.', 'hrách',
             'kukuřice', 'oves', 'jetel_I', 'jetel_II', 'jetel_III',
             'pšenice', 'ječmen oz.', 'brambory', 'ječmen j.',
             'hrách', 'kukuřice', 'oves', 'jetel_I']
    df_plodiny_pole = pd.DataFrame({"ID":IDs, "Names":names})

    # Crop rotation
    crops_tab = pd.DataFrame({"ID_set":[0, 1, 100, 100, 100, 5, 4, 9, 3,
                                        8],
                                    "osev":[4,9,3,5,7,4,4,8,3,4],
                                 "sklizeň":[7,7,5,7,9,9,7,9,9,8]})

    crops_params = pd.DataFrame({"ID_set":[0, 1, 20, 21, 12, 5, 4,
                                           9, 3,
                                        8],
                                 "osev":[4,9,4,9,9,4,4,8,3,4],
                                 "sklizeň":[7,7,8,8,7,9,7,9,9,8],
                                 "DW_max":[12,15,24,11,7,8,9,6,14,7],
                                 "LAI_max": [5,5,5,5,5,5,5,5,5,5,],
                                 "R_max":[95,95,95,95,95,95,95,95,95,
                                          95],
                                 "R_min":[25,24,25,30,45,17,15,18,25,
                                          70],
                                 "Koef_m":[13.4,14,15,13,14,11,12,15,
                                           17,13],
                                 "Koef_n":[4.2,3.6,4,5,8,3,4,5,6,4]})

    # Calculation
    sp = SowingProcTimeSeries()

    t1 = time.time()

    ts_all = sp.predictCropsRotation(crops_tab, 0, 1, 2, 190, 6, False)

    dw_TS = sp.predictDryMass(crops_tab, crops_params, 0, 1, 2, 90,
                              6, False)
    harvest = sp.predictHarvest(crops_tab, 0, 1, 2, 190, 6, False)

    t2 = time.time()
    print(t2-t1)

    dw_TS_transp = harvest.T
    jmena = dw_TS_transp.iloc[0,:]
    dw_TS_transp.columns = jmena
    dw_new = dw_TS_transp.drop(dw_TS_transp.index[0])

    xxx = dw_new.iloc[:,1]
    yyy = dw_new.iloc[:,2]

    plt.plot(xxx)

    plt.show()

    print(ts_all)

