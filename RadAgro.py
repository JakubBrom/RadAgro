# -*- coding: utf-8 -*-

#  Project: RadAgro
#  File: RadAgro.py
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
#  Last changes: 28.12.20 16:46
#
#  Begin: 2020/10/23


from qgis.PyQt.QtCore import QSettings, QTranslator, \
    QCoreApplication, Qt, QUrl, QDate, QThread, QObject
from qgis.PyQt.QtGui import QIcon, QDesktopServices, QPixmap
from qgis.PyQt.QtWidgets import QAction, QComboBox, \
    QPushButton, QMessageBox, QTableWidgetItem, QDateEdit, \
    QVBoxLayout, QDoubleSpinBox, QCompleter, QProgressBar, \
    QDialogButtonBox

# Initialize Qt resources from file resources.py
from .resources import * # TODO

from qgis.core import Qgis, QgsMapLayerProxyModel, QgsProject, \
    QgsVectorLayer

# Import the code for the dialog
from .RadAgro_dialog import RadAgroDialog    # TODO

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as \
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import os.path
import numpy as np
import pandas as pd
import datetime
import traceback
import sys

# Import modules    # TODO
from .modules.SARCA_lib import SARCALib
from .modules.sowing_proc import SowingProcTimeSeries
from .modules.activity_decay import ActivityDecay
from .modules.usle import RadUSLE
from .modules.overlap_clip import *
from .modules.hydrIO import *
from .modules.zonal_stats import *

sl = SARCALib()
sp = SowingProcTimeSeries()
ad = ActivityDecay()
ru = RadUSLE()


class RadAgro:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):

        """Constructor.

        :param iface: An interface instance that will be passed to
        this class which provides the hook by which you can
        manipulate the QGIS application at run time.
        :type iface: QgsInterface
        """

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        self.locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RadAgro_{}.qm'.format(self.locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&RadAgro')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.pluginIsActive = False
        self.dlg = None

        # Read constants
        self.constants()
        self.df_radio_contamination = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('RadAgro', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/RadAgro/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'RadAgro'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if not self.pluginIsActive:
            self.pluginIsActive = True
            self.dlg = RadAgroDialog()

        # Help
        self.dlg.button_box.helpRequested.connect(self.pluginHelp)

        # Set disabled OK dialog button
        self.dlg.button_box.button(QDialogButtonBox.Ok).setEnabled(
            False)

        # Run results calculation
        self.dlg.button_box.accepted.connect(self.resultsRun)

        # Set initial index of cbox_precip as 0
        self.dlg.cbox_precip.setCurrentIndex(0)

        # Add rows to sowing procedure table
        self.dlg.pb_sow_plus.clicked.connect(lambda:
                                             self.cropTableAddRow(
                                                 self.dlg.tw_sowing))
        
        # Add rows to meadows table
        self.dlg.pb_meadow_plus.clicked.connect(lambda:
                                             self.meadowTableAddRow(
                                                 self.dlg.tw_meadow))

        # Remove rows from sowing proc table
        self.dlg.pb_sow_minus.clicked.connect(lambda:
                                              self.tableRemoveRow(
                                                  self.dlg.tw_sowing))

        # Remove rows from meadow table
        self.dlg.pb_meadow_minus.clicked.connect(lambda:
                                              self.tableRemoveRow(
                                                  self.dlg.tw_meadow))

        # Create figure after fid selection
        self.dlg.cbox_ID_select.currentIndexChanged.connect(self.plot)
        self.dlg.cbox_y_scale.currentIndexChanged.connect(self.plot)

        # Create plot
        self.figure = plt.figure(facecolor="white")  # create plot
        self.canvas = FigureCanvas(self.figure)
        # toolbar = NavigationToolbar(self.canvas, self)

        # Add plot in to UI widget
        lay = QVBoxLayout(self.dlg.widget_plot)
        lay.setContentsMargins(0, 0, 0, 0)
        # lay.addWidget(toolbar)
        lay.addWidget(self.canvas)
        # self.setLayout(lay)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&RadAgro'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        # print "** STARTING UrbanSARCA"
        self.showInfo()

        # set tab with graph disabled
        self.dlg.tabWidget.setTabEnabled(2, False)

        # Hide hydrology tabs
        self.dlg.toolBox.setItemEnabled(1, False)
        self.dlg.toolBox_2.setItemEnabled(5, False)

        # Set type of input to input cboxes
        self.dlg.cbox_rad_depo.setFilters(
            QgsMapLayerProxyModel.RasterLayer)
        self.dlg.cbox_precip.setFilters(
            QgsMapLayerProxyModel.RasterLayer)
        self.dlg.cbox_crop_lyr.setFilters(
            QgsMapLayerProxyModel.PolygonLayer)
        self.dlg.cbox_HPJ.setFilters(
            QgsMapLayerProxyModel.PolygonLayer)
        self.dlg.cbox_dmt.setFilters(
            QgsMapLayerProxyModel.RasterLayer)

        # If precipitation is constant the cbox for precipitation
        # raster is empty
        self.dlg.rb_precip_konst.toggled.connect(lambda:
                self.setCboxEmpty(self.dlg.cbox_precip))
        self.dlg.rb_precip_rast.toggled.connect(lambda:
            self.dlg.cbox_precip.setCurrentIndex(0))
        # If raster of precipitation is selected, value in spinbox is set
        # to 0.0
        self.dlg.rb_precip_rast.toggled.connect(lambda:
            self.dlg.sbox_precip.setValue(0.00))

        # Set fields from crop layer to fieldCbox
        self.dlg.cbox_crop_lyr.layerChanged.connect(lambda:
                                                    self.setKeyField(
                                                        self.dlg.cbox_crop_lyr, self.dlg.cbox_crop_lyr_key))
        #
        # # Set fields from crop layer to fieldCbox
        # self.dlg.cbox_crop_lyr.layerChanged.connect(lambda:
        #                                             self.setKeyField(
        #                                                 self.dlg.cbox_crop_lyr, self.dlg.cbox_ID))

        # Set fields from HPJ layer to fieldCbox
        self.dlg.cbox_HPJ.layerChanged.connect(lambda:
                                                    self.setKeyField(
                                                        self.dlg.cbox_HPJ, self.dlg.cbox_HPJ_key))

        # Set particular crops defined by user to tw_crops_orig table
        self.dlg.cbox_crop_lyr_key.fieldChanged.connect(lambda:
                                           self.setOrigCropsToTable())

        # Set IDs of fields to cbox_select_ID
        self.dlg.cbox_crop_lyr.layerChanged.connect(lambda: self.readIDField())

        # Set soil saturation during the year
        self.setClimateTable()

        # Set parameters of the crops
        self.dlg.pb_params.clicked.connect(lambda: self.fillParams())

        # Set default slope and intercept coefficients of the growth
        # model to growth model table for particular
        self.dlg.pb_coefs.clicked.connect(lambda: self.calculateGowthCurveCoefs())

        # show the dialog
        self.dlg.show()

#-----------------------------------------------------------------------
# Calculation

    def resultsRun(self):
        """Run the process of calculation in threads"""

        # Read constants from UI
        self.readConstants()
        # Read HPJ field
        self.su_field = self.dlg.cbox_HPJ_key.currentField()
        # Run Working thread
        self.startWorker()

    def resultsCalculate(self):
        """Running the calculation without threading and progress bar
        showing."""

        # Main soil units layer path and field name
        su_lyr_path = self.getLyrPath(self.dlg.cbox_HPJ)
        su_field = self.dlg.cbox_HPJ_key.currentField()

        # Crops layer path
        crops_path = self.getLyrPath(self.dlg.cbox_crop_lyr)

        # Load rasters of radioactivity, precip. and DMT and clip to
        # the overlapping area with the smallest pixel
        depo_path, precip_path, dmt_path = self.loadRasters()

        # Loading crops layer and creating initial crops dataframe
        df_crops_init = self.createCropsInitDf(crops_path)

        # Read crops growth model data from UI
        df_growth_model_params = self.readGrowthModelParams()

        # Read transfer coefficients from UI
        df_transf_coefs = self.readTransferCoef()

        # Calculate early stage
        self.earlyStage(depo_path, precip_path, crops_path, 
                        df_crops_init)

        # Read crops rotation data and meadows cutting data from UI
        df_crops_rotation = self.readCropsRotation()
        df_meadows = self.readMeadowsCut()

        # Create time series for crops
        df_crops_rotation_all = self.createCropsRotationTS(
            df_crops_init, df_crops_rotation, df_meadows)
        df_crops_harvest = self.createCropsHarvestTS(df_crops_init,
                                                          df_crops_rotation,
                                                          df_meadows)
        df_crops_dw_all = self.createDryMassTS(df_crops_init,
                                                    df_growth_model_params,
                                                    df_crops_rotation,
                                                    df_meadows)

        # Calculate USLE
        k_factor_tab = self.readKFactorTable()
        k_factor = ru.fK(su_lyr_path, su_field, k_factor_tab,
                         crops_path)
        ls_factor = ru.fLS(dmt_path, crops_path, self.ls_factor_m,
                           self.ls_factor_n)
        c_factor_tab = self.readCFactorTable()
        r_perc = self.readRFactorPercTable()

        # Calculate hydrology
        # TODO

        # Calculate total radioactive contamination time series table
        self.calculateRadioactiveContamination(df_transf_coefs,
                                               df_crops_rotation_all,
                                               df_crops_harvest,
                                               df_crops_dw_all,
                                               k_factor, ls_factor,
                                               c_factor_tab, r_perc)

        # Export data
        # self.exportTablesToCsv()        # Export to csv
        self.exportRadioCont2GeoPackage()

        # The page with graph enabled
        self.dlg.tabWidget.setTabEnabled(2, True)

        return

    def readConstants(self):
        """Read all constants from UI"""

        # Date of radiation accident
        self.accident_date = self.dlg.de_accident.date()
        self.accident_jul = self.accident_date.dayOfYear()

        # Early stage management
        self.early = self.dlg.chbox_management.isChecked()

        # Date of prediction
        self.predict_date = self.dlg.de_predict.date()
        self.predict_no_months = 12 - self.accident_date.month() + (
            self.predict_date.year()-self.accident_date.year()-1)*12 + \
                                 self.predict_date.month()
        self.first_month = self.accident_date.month()

        # Reference levels of radioactivity contamination
        self.rl_1 = int(self.dlg.sbox_ru1.value())
        self.rl_2 = int(self.dlg.sbox_ru2.value())

        # Coefficients for interception factor calculation
        self.radionuclide = self.dlg.cbox_contaminant.currentIndex()
        if self.radionuclide == 0:
            self.coef_k = 1.0       # Cs
        else:
            self.coef_k = 2.0       # Sr

        self.coef_S = 0.2

        # Precipitation amount during radioactivity deposition
        self.precip_const = self.dlg.sbox_precip.value()

        # Erosion constants
        self.r_factor_const = self.dlg.sbox_r_factor.value()
        self.ls_factor_m = self.dlg.sbox_LS_m.value()
        self.ls_factor_n = self.dlg.sbox_LS_n.value()
        self.p_factor = self.dlg.sbox_P_fact.value()
        self.soil_depth = self.dlg.sbox_soil_depth.value()
        self.soil_vol_mass = self.dlg.sbox_vol_soil.value()

    def loadRasters(self):
        """Reading rasters of radioactivity deposition, precipitation
        and DMT."""

        # Read original rasters
        depo_path = self.getLyrPath(self.dlg.cbox_rad_depo)
        precip_path = self.getLyrPath(self.dlg.cbox_precip)
        dmt_path = self.getLyrPath(self.dlg.cbox_dmt)

        # Clipping the rasters
        if precip_path != None and precip_path != "":
            in_lyrs = [depo_path, precip_path, dmt_path]
            (depo_path_new, precip_path_new, dmt_path_new) = \
                clipOverlappingArea(in_lyrs, tmp_out=True)

        else:
            in_lyrs = [depo_path, dmt_path]
            (depo_path_new, dmt_path_new) = \
                clipOverlappingArea(in_lyrs, tmp_out=True)
            precip_path_new = None

        # Get temporary folder path
        self.tmp_folder = os.path.dirname(depo_path_new)

        return depo_path_new, precip_path_new, dmt_path_new

    def createCropsInitDf(self, crops_path):
        """Read indices of crops corresponding to original crops from
        tw_crops_orig table and write them to the initial vector
        layer

        :param crops_path: path to crops vector layer

        :return: initial dataframe for crops and following
            calculation results
        """

        # Get number of rows in the table
        r_count = self.dlg.tw_crops_orig.rowCount()

        # Read original IDs (keys) and newly set IDs for particular crops
        # from the tw_crops_orig table
        crops_IDs_orig_list = [self.dlg.tw_crops_orig.item(i,0).text()
                   for i in range(r_count)]
        crops_IDs = [self.dlg.tw_crops_orig.cellWidget(i,1).currentIndex()
                   for i in range(r_count)]
        crops_names = [self.dlg.tw_crops_orig.cellWidget(i,1).currentText()
                   for i in range(r_count)]

        df_crops_coupling = pd.DataFrame({"ID_orig":crops_IDs_orig_list,
                                       "ID_set":crops_IDs, self.tr(
                "Name"):crops_names})

        # Load crops layer to qgis
        crops_lyr = QgsVectorLayer(crops_path, self.tr(
            "Crops_orig"), "ogr")

        # Read original crops IDs from crop vector - for all rows
        crop_IDs_field_name = self.dlg.cbox_crop_lyr_key.currentText()
        crops_IDs_orig_list_all = []
        for feature in crops_lyr.getFeatures():
            crops_IDs_orig_list_all.append(feature[crop_IDs_field_name])

        # Read FID field from crop layer
        crops_fid = []
        for feature in crops_lyr.getFeatures():
            crops_fid.append(feature.id())

        # Calculate area of fields in the vector layer
        crops_area_ha = []
        for feature in crops_lyr.getFeatures():
            crops_area_ha.append(feature.geometry().area()/10000)

        # Create new Pandas dataframe containing IDs of fields,
        # crops_IDs and crops_names corresponding to the vector layer
        df_crops_rows = pd.DataFrame({"fid":crops_fid,
                                      "ID_orig":crops_IDs_orig_list_all,
                                      self.tr("Area_ha"):crops_area_ha})

        # Merge df_crops_coupling and df_crops_rows to initial dataframe
        df_crops_init = pd.merge(df_crops_rows, df_crops_coupling,
                                      how="left", on="ID_orig")

        return df_crops_init

    def earlyStage(self, depo_path, precip_path, crops_path,
                   df_crops_init):
        """Calculation of radioactive contamination in early stage of
        radioactive accident.

        :param depo_path: Path to raster with deposition
            :math:`(Bq.m^{-1})`
        :param precip_path: Path to raster with precipitation (mm)
        :param crops_path: Path to crops vector layer
        :param df_crops_init: Initial crops dataframe
        """

        # Create df for radioactive contamination
        self.df_radio_contamination = df_crops_init.copy(True)

        # Calculation of total deposition for all fields in the area of interest
        total_depo_zonal = pd.DataFrame(zonal_stats(crops_path,
                                       depo_path, method="median"))
        total_deposition = np.array(total_depo_zonal["median"])
        total_deposition = np.nan_to_num(total_deposition)
        total_deposition = np.where(total_deposition < 0.0, 0.0, total_deposition)

        # Add initial total deposition to df
        self.df_radio_contamination["Tot_depo"] = total_deposition

        # Create df for reference levels
        self.df_ref_levels = df_crops_init.copy(True)

        # Calculated Ref.levels and add them to df
        ref_levels = sl.referLevel(total_deposition, self.rl_1, self.rl_2)

        self.df_ref_levels["Init_Ref_levels"] = ref_levels

        # Calculates total radioactive contamination after biomass removing
        # in early stage of radioactive contamination
        if self.dlg.chbox_management.isChecked():
            # Reading data from tw_growth_params table
            r_count = self.dlg.tw_growth_params.rowCount()

            model_IDs = np.array([self.dlg.tw_growth_params.item(i,0).text()
                       for i in range(r_count)]).astype(int)
            model_sowing = np.array([self.dlg.tw_growth_params.cellWidget(i,2)
                            .date().dayOfYear() for i in range(
                r_count)]).astype(int)
            model_harvest = np.array([self.dlg.tw_growth_params.cellWidget(i,3)
                            .date().dayOfYear() for i in range(
                r_count)]).astype(int)
            model_DWmax = np.array([self.dlg.tw_growth_params.item(i,4).text()
                       for i in range(r_count)]).astype(float)
            model_LAImax = np.array([self.dlg.tw_growth_params.item(i,5).text()
                       for i in range(r_count)]).astype(float)
            model_R_min = np.array([self.dlg.tw_growth_params.item(i,7).text()
                       for i in range(r_count)]).astype(float)
            model_coef_m = np.array([self.dlg.tw_growth_params.item(i,8).text()
                       for i in range(r_count)]).astype(float)
            model_coef_n = np.array([self.dlg.tw_growth_params.item(i,9).text()
                       for i in range(r_count)]).astype(float)

            # Calculation of dry mass of biomass and LAI for accident date
            actual_DW = sl.dryMass(model_DWmax, self.accident_jul,
                                   model_sowing, model_harvest, model_coef_m,
                                   model_coef_n)
            actual_LAI = sl.leafAreaIndex(actual_DW, model_DWmax,
                                          model_LAImax, model_R_min,
                                          self.accident_jul, model_sowing,
                                          model_harvest)

            # Create table with results for dw_act and LAI
            dw_lai_table = pd.DataFrame({"ID_set":model_IDs, "dw_act":actual_DW,
                                         "LAI":actual_LAI})

            # Join dw_act and LAI to new df corresponding with the input vector
            # layer
            df_dw_lai_all = pd.merge(df_crops_init, dw_lai_table,
                                     on="ID_set", how="left")

            # Calculation of soil contamination
            # Precipitation
            if precip_path != None and precip_path != "":
                actual_prec_zonal = zonal_stats(crops_path,
                                            precip_path, method="median")
                actual_precip = np.array([actual_prec_zonal[i]["median"] for
                                    i in range(len(actual_prec_zonal))])
            else:
                actual_precip = self.precip_const

            # IF
            intercept_factor = sl.interceptFactor(df_dw_lai_all["LAI"],
                                                  actual_precip,
                                                  df_dw_lai_all["dw_act"],
                                                  self.coef_k, self.coef_S)
            intercept_factor = np.where(ref_levels == 2, 0,
                                        intercept_factor)

            # Soil contamination
            reduced_cont = sl.contSoil(total_deposition, intercept_factor)
            reduced_cont = np.nan_to_num(reduced_cont)
            reduced_cont = np.where(reduced_cont < 0.0, 0.0, reduced_cont)

        else:
            reduced_cont = total_deposition

        # Add reduced radioactive contamination amount to df
        self.df_radio_contamination["Depo_red"] = reduced_cont

    def readGrowthModelParams(self):
        """Read data from growth model table and add it to df"""

        r_count = self.dlg.tw_growth_params.rowCount()

        model_IDs = np.array(
            [self.dlg.tw_growth_params.item(i, 0).text()
             for i in range(r_count)]).astype(int)
        model_sowing = np.array(
            [self.dlg.tw_growth_params.cellWidget(i, 2)
            .date().dayOfYear() for i in range(
                r_count)]).astype(int)
        model_harvest = np.array(
            [self.dlg.tw_growth_params.cellWidget(i, 3)
            .date().dayOfYear() for i in range(
                r_count)]).astype(int)
        model_DWmax = np.array(
            [self.dlg.tw_growth_params.item(i, 4).text()
             for i in range(r_count)]).astype(float)
        model_LAImax = np.array(
            [self.dlg.tw_growth_params.item(i, 5).text()
             for i in range(r_count)]).astype(float)
        model_R_max = np.array(
            [self.dlg.tw_growth_params.item(i, 6).text()
             for i in range(r_count)]).astype(float)
        model_R_min = np.array(
            [self.dlg.tw_growth_params.item(i, 7).text()
             for i in range(r_count)]).astype(float)
        model_coef_m = np.array(
            [self.dlg.tw_growth_params.item(i, 8).text()
             for i in range(r_count)]).astype(float)
        model_coef_n = np.array(
            [self.dlg.tw_growth_params.item(i, 9).text()
             for i in range(r_count)]).astype(float)

        df_growth_model_params = pd.DataFrame({
            "ID_set":model_IDs, "sow":model_sowing,
            "harv":model_harvest, "DW_max":model_DWmax,
            "LAI_max":model_LAImax, "R_max":model_R_max,
            "R_min":model_R_min, "coef_m":model_coef_m,
            "coef_n":model_coef_n})

        return df_growth_model_params

    def readCropsRotation(self):
        """Get data from UI for crops rotation and their preparation
        for next calculation"""

        # No of counts in table
        r_count = self.dlg.tw_sowing.rowCount()

        # Read data
        rotation_IDs = np.array([self.dlg.tw_sowing.cellWidget(i,0)
            .currentIndex() for i in range(r_count)]).astype(int)
        crops_sowing = np.array([self.dlg.tw_sowing.cellWidget(i, 1)
            .currentText() for i in range(r_count)]).astype(int)
        crops_harvest = np.array([self.dlg.tw_sowing.cellWidget(i, 2)
            .currentText() for i in range(r_count)]).astype(int)

        # Create dataframe from the data
        df_crops_rotation = pd.DataFrame({"ID_set":rotation_IDs,
                                          "sow":crops_sowing,
                                          "harv":crops_harvest})

        return df_crops_rotation

    def readTransferCoef(self):
        """Reading transfer coefficient table fro UI"""

        # Calculate no. of rows
        r_count = self.dlg.tw_radio_coefs.rowCount()

        # Read data
        IDs = np.array([self.dlg.tw_radio_coefs.item(i,0).text() for i
                        in range(r_count)]).astype(int)
        transf_coefs = np.array([self.dlg.tw_radio_coefs.item(i,
                        2).text() for i in range(r_count)]).astype(
                        float)

        # Create dataframe from the data
        df_transf_coefs = pd.DataFrame({"ID_set": IDs,
                                          "TK": transf_coefs})

        return df_transf_coefs

    def readMeadowsCut(self):
        """Get data from UI for meadows mowing and their preparation
        for next calculation"""

        # No of columns in table
        r_count = self.dlg.tw_meadow.rowCount()

        # In case of IDs, the values are increased to 100+ because
        # the resolution of the meadows cuts in TS
        meadows_IDs = np.array([self.dlg.tw_meadow.cellWidget(i, 0)
                               .currentIndex() + 100 for i in
                                range(r_count)]).astype(int)
        meadows_cut = np.array([self.dlg.tw_meadow.cellWidget(i, 1)
                                .currentText() for i in
                                 range(r_count)]).astype(int)

        # Start of meadows growing after mowing. Start in spring is
        # 1th March
        meadows_sowing = [3]
        for i in range(len(meadows_IDs)-1):
            meadows_sowing.append(meadows_cut[i])

        df_meadows = pd.DataFrame({"ID_set":meadows_IDs,
                                          "sow":meadows_sowing,
                                          "harv":meadows_cut})

        return df_meadows

    def createCropsRotationTS(self, df_crops_init, df_crops_rotation,
                              df_meadows):
        """Create time series for crops and meadows rotation for the
        area of interest.

        :param df_crops_init: Initial dataframe for crops
        :param df_crops_rotation: Dataframe with crops rotation
        :param df_meadows: Dataframe with rotation of meadows mowing
        """

        # Create table for writing data
        df_rotation_init = df_crops_init.copy(True)

        # Create df for all crops in the crops rotation
        df_crops_rot = sp.predictCropsRotation(df_crops_rotation,
                            ID_col_number=0, sowing_col_number=1,
                            harvest_col_number=2,
                            predict_months=self.predict_no_months,
                            start_month=self.first_month,
                            early_stage_mng=self.early)

        # Create df for mowing meadows
        df_meadows_rot = sp.predictCropsRotation(df_meadows,
                            ID_col_number=0, sowing_col_number=1,
                            harvest_col_number=2,
                            predict_months=self.predict_no_months,
                            start_month=self.first_month,
                            early_stage_mng=self.early)

        # Change ID of the meadows TS to 20 (set in data as meadows)
        df_meadows_rot["ID_set"][0] = 20
        df_meadows_rot = pd.DataFrame(df_meadows_rot.iloc[0:1])
        df_meadows_rot[df_meadows_rot > 99] = 20

        # Merge crops and meadows data together
        df_all_crops = pd.concat([df_crops_rot, df_meadows_rot],
                                 ignore_index=True)

        # Merge TS to vector data layer for whole area of interest
        df_crops_rotation_all = pd.merge(df_rotation_init,
                                          df_all_crops, how='left',
                                          on='ID_set', sort=False)

        return df_crops_rotation_all

    def createCropsHarvestTS(self, df_crops_init, df_crops_rotation,
                             df_meadows):
        """Create time series of the harvest time for the area of
        interest
        :param df_meadows: Dataframe with meadows mowing time series
        :param df_crops_rotation: Dataframe with crops rotation time
        series
        :param df_crops_init: Initial crops rotation dataframe
        """

        # Create tables for writing data
        df_harvest_init = df_crops_init.copy(True)

        # Create df for all crops in the crops rotation
        df_crops_harvest = sp.predictHarvest(df_crops_rotation,
                            ID_col_number=0, sowing_col_number=1,
                            harvest_col_number=2,
                            predict_months=self.predict_no_months,
                            start_month=self.first_month,
                            early_stage_mng=self.early)

        # Create df for mowing meadows
        df_meadows_harvest = sp.predictHarvest(df_meadows,
                            ID_col_number=0, sowing_col_number=1,
                            harvest_col_number=2,
                            predict_months=self.predict_no_months,
                            start_month=self.first_month,
                            early_stage_mng=self.early)

        # Change ID of the meadows TS to 20 (set in data as meadows)
        df_meadows_harvest["ID_set"][0] = 20
        df_meadows_harvest = pd.DataFrame(df_meadows_harvest.iloc[0:1])

        # Merge crops and meadows data together
        df_all_harvest = pd.concat([df_crops_harvest,
                                    df_meadows_harvest],
                                    ignore_index=True)

        # Merge TS to vector data layer for whole area of interest
        df_crops_harvest = pd.merge(df_harvest_init,
                                         df_all_harvest, how='left',
                                         on='ID_set', sort=False)

        return df_crops_harvest

    def createDryMassTS(self, df_crops_init, df_growth_model_params,
                        df_crops_rotation, df_meadows):
        """Create time series table for dry weight of the crops for
        the area of interest
        
        :param df_meadows: Dataframe with meadows mowing time series
        :param df_crops_rotation: Dataframe with crops rotation time
            series
        :param df_growth_model_params: Dataframe with parameters of
            growth model
        :param df_crops_init: Initial crops rotation time series
            dataframe.
        """

        # Create table for writing data
        df_dw_init = df_crops_init.copy(True)

        # Create df for all crops in the crops rotation
        df_crops_dw = sp.predictDryMass(df_crops_rotation,
                                             df_growth_model_params,
                                             ID_col_number=0,
                                             sowing_col_number=1,
                                             harvest_col_number=2,
                                             predict_months=self.predict_no_months,
                                             start_month=self.first_month,
                                             early_stage_mng=self.early)

        # Create df for mowing meadows
        df_meadows_dw = sp.predictDryMass(df_meadows,
                                               df_growth_model_params,
                                               ID_col_number=0,
                                               sowing_col_number=1,
                                               harvest_col_number=2,
                                               predict_months=self.predict_no_months,
                                               start_month=self.first_month,
                                               early_stage_mng=self.early)

        # Change ID of the meadows TS to 20 (set in data as meadows)
        df_meadows_dw.loc[0, "ID_set"] = 20
        df_meadows_dw = pd.DataFrame(df_meadows_dw.iloc[0:1])
        # Merge crops and meadows data together
        df_all_dw = pd.concat([df_crops_dw, df_meadows_dw],
                              ignore_index=True)
        # Merge TS to vector data layer for whole area of interest
        df_crops_dw_all = pd.merge(df_dw_init, df_all_dw,
                                        how='left', on='ID_set',
                                        sort=False)

        return df_crops_dw_all

    def readRFactorPercTable(self):
        """Read table with percentage of R factor throughout the
        year."""

        # Read number of columns in table
        n_cols = self.dlg.tw_r_factor_perc.columnCount()

        r_perc = np.array([self.dlg.tw_r_factor_perc.item(0,
                    i).text() for i in range(n_cols)]).astype(float)

        return r_perc

    def readKFactorTable(self):
        """Read R factors values of USLE equation corresponding to Main
        Soil Units (MSU) according to Janeček et al. 2007. The first
        column of output is MSU, the second is K factor of USLE
        equation."""

        # No of counts in table
        r_count = self.dlg.tw_HPJ_params.rowCount()

        # Read data
        su_values = np.array([self.dlg.tw_HPJ_params.item(i, 0).text()
                              for i in range(r_count)]).astype(int)
        k_factor_values = np.array([self.dlg.tw_HPJ_params.item(i,
                        2).text() for i in range(r_count)]).astype(
                        float)

        df_k_factor = pd.DataFrame({"MSU":su_values,
                                         "K_factor":k_factor_values})

        return df_k_factor

    def readCFactorTable(self):
        """Read C factors values of USLE equation corresponding to
        particular crops according to Janeček et al. 2007. The first
        column of output is crop ID, the second is C factor of USLE
        equation."""

        # No of counts in table
        r_count = self.dlg.tw_C_factor.rowCount()

        # Read data
        crops_values = np.array([self.dlg.tw_C_factor.item(i, 0).text()
                              for i in range(r_count)]).astype(int)
        c_factor_values = np.array([self.dlg.tw_C_factor.item(i,
                2).text() for i in range(r_count)]).astype(float)

        df_c_factor = pd.DataFrame({"ID_set": crops_values,
                                         "C_factor": c_factor_values})

        # Add values for bare soil
        df_bare_soil = pd.DataFrame({"ID_set":[-999], "C_factor":[0.9]})

        df_c_factor = pd.concat([df_c_factor, df_bare_soil], ignore_index=True)

        return df_c_factor

    def calculateRadioactiveContamination(self, df_transf_coefs,
                                          df_crops_rotation_all,
                                          df_crops_harvest,
                                          df_crops_dw_all, k_factor,
                                          ls_factor, c_factor_tab,
                                          r_perc):
        """Calculation of total radioactive contamination of
        particular fields

        :param df_transf_coefs: Dataframe with transfer coefficient
            extracted from UI
        :param df_crops_rotation_all: Dataframe with crops rotation
            time series
        :param df_crops_harvest: Dataframe with harvests time series
        :param df_crops_dw_all: Dataframe with dry weight of biomass
            time series
        :param k_factor: Dataframe with K factor of USLE values
        :param ls_factor: Dataframe with LS factor of USLE values
        :param c_factor_tab: Dataframe with C factor of USLE values
        :param r_perc: Percentage of R factor during the year
        """

        # Calculation cycle of total radioactive contamination (RC) for
        # prediction time series
        for i in range(self.predict_no_months):
            # Month name
            month_name = "M{no}".format(no=str(i+1))

            # Extraction of current month number
            acc_day = copy.deepcopy(self.accident_date)
            current_date = acc_day.addMonths(i + 1)
            current_month = current_date.month()

            # 1. Read RC from previous month
            radio_cont_tot_init = np.array(
                self.df_radio_contamination.iloc[:,i+6])

            # 2. Read column for harvest
            harvest = np.array(df_crops_harvest.iloc[:,i+5])
            harvest = np.nan_to_num(harvest)

            # 3. Read dry mass of crops
            dry_mass = np.array(df_crops_dw_all.iloc[:,i+5])
            dry_mass = np.nan_to_num(dry_mass)

            # 4. Merge Tk to actual crops
            crops_act = df_crops_rotation_all.iloc[:,i+5]
            crops_act = pd.DataFrame({"ID_set":crops_act})
            df_transf_coefs_all = pd.merge(crops_act,
                                           df_transf_coefs,
                                           on="ID_set", how="left")
            tr_coefs_arr = np.array(df_transf_coefs_all.iloc[:,1])
            tr_coefs_arr = np.nan_to_num(tr_coefs_arr)

            # 5. Calculation of radioactive contamination reduced by
            # crops biomass removing
            radio_cont_tot = radio_cont_tot_init - radio_cont_tot_init\
                             * dry_mass * 0.1 * tr_coefs_arr * harvest

            # 6. Apply reference levels - combine RLs with new values
            ref_levels = np.array(self.df_ref_levels.iloc[:,i+5])
            radio_cont_tot = np.where(ref_levels == 2,
                                      radio_cont_tot_init,
                                      radio_cont_tot)
            radio_cont_tot = np.nan_to_num(radio_cont_tot)

            # 7. Hydrology - reducing radioactivity by outflow of
            # TODO: doplnit celou hydrologii
            radio_cont_tot = radio_cont_tot * (1)     # TODO

            # 8. Erosion - reducing radioactive contamination by
            # erosion
            # R factor
            r_factor = ru.fR(self.r_factor_const, r_perc[current_month-1])

            # C factor
            c_factor = pd.merge(crops_act, c_factor_tab, how="left",
                                on="ID_set")

            # Water erosion in t/ha/month
            usle_all = r_factor * ls_factor.iloc[:,1]\
                    * k_factor.iloc[:,1] * c_factor["C_factor"] * \
                    self.p_factor

            # USLE for reference level 3
            usle_r3 = r_factor * ls_factor.iloc[:,
                                 1] * k_factor.iloc[:,1] * 0.1

            usle = np.where(ref_levels == 2, usle_r3, usle_all)

            # Dry soil mas for mixture layer (ca 0.2 m; kg)
            soil_mass = self.soil_depth * self.soil_vol_mass

            # Activity released by water erosion
            radio_usle = radio_cont_tot * usle * 0.1/soil_mass

            radio_cont_tot = radio_cont_tot - radio_usle

            # 9. Radioactive decay
            # Replace nans in RC by init RC
            radio_cont_tot = np.nan_to_num(radio_cont_tot)
            radio_cont_tot = np.where(radio_cont_tot == 0,
                                radio_cont_tot_init, radio_cont_tot)

            # Calculate radioactivity decay
            radio_cont_tot = ad.activityDecay(radio_cont_tot,
                                              current_month,
                                              self.radionuclide)

            # 10. Add data to df with radioactive contamination
            self.df_radio_contamination[month_name] = radio_cont_tot

            # 11. Create new reference levels and add it to df
            new_ref_levels = sl.referLevel(radio_cont_tot, self.rl_1,
                                           self.rl_2)
            self.df_ref_levels[month_name] = new_ref_levels

    # def exportTablesToCsv(self):
    #     """Exporting tables created by RadAgro to csv"""
    # 
    #     # TODO: zatim se budou data ukládat do /home, následně bude export do
    #     #  gdpg - všechny vrstvy do jedný databáze
    # 
    #     self.df_radio_contamination.to_csv("kontam.csv")
    #     self.df_ref_levels.to_csv("RU.csv")
    #     df_crops_rotation_all.to_csv("OP.csv")
    #     self.df_crops_harvest.to_csv("Sklizne.csv")
    #     df_crops_dw_all.to_csv("susina.csv")

    def exportRadioCont2GeoPackage(self):
        """Export dataframe with radioactive contamination to
        Geo Package (gpkg)."""

        in_lyr = self.getLyrPath(self.dlg.cbox_crop_lyr)
        out_lyr_path = self.dlg.out_file.filePath()

        joinLyrWithDataFrame(in_lyr, self.df_radio_contamination,
                             out_lyr_path)

    def getLyrPath(self, comboBox):
        """Get path to input file from combobox

        :param comboBox: combo box in UI.
        :retrun: path to input file"""

        try:
            get_index = comboBox.currentIndex()
            get_path = comboBox.layer(get_index).source()
        except Exception:
            get_path = comboBox.currentText()

        return get_path

#-----------------------------------------------------------------------
# UI manipulation

    def readIDField(self):
        """Read  IDs for particular fileds in the area of interest
        and set the data to select_ID combobox for generating plots
        with reults"""

        # TODO: solve a shift of ID values 1 --> 0 in case of shapefile
        #  without FID

        # Clear cbox
        self.dlg.cbox_ID_select.clear()

        # Get data from vector file for ID field
        map_lyr = self.dlg.cbox_crop_lyr.currentLayer()

        self.crop_ID_list = []
        for feature in map_lyr.getFeatures():
            self.crop_ID_list.append(feature.id())

        values_list = [str(self.crop_ID_list[i]) for i in range(len(
            self.crop_ID_list))]

        # Set IDs to cbox
        self.dlg.cbox_ID_select.addItems(values_list)
        self.dlg.cbox_ID_select.setEditable(True)
        # Set completer for cbox
        completer = QCompleter(values_list)
        self.dlg.cbox_ID_select.setCompleter(completer)

    def plot(self):
        "Create plot in the UI"

        # TODO: vložit do grafu nástroje na analýzu a hodnocení grafu

        # Data
        ignore_zero = np.seterr(all="ignore")

        # Clear last figure
        self.figure.clear()

        if self.df_radio_contamination is not None:
            # Get position in the table
            pl_ID_text = self.dlg.cbox_ID_select.currentText()
            pl_ID = int(pl_ID_text)

            # get data for plotting from selected row (polygon)
            y_row = self.df_radio_contamination.loc[
                self.df_radio_contamination['fid'] == pl_ID]
            y = y_row.iloc[0, 5:]

        else:
            pl_ID_text = self.dlg.cbox_ID_select.currentText()
            x = [1]
            y = [1]

        # with plt.xkcd():
        # create an axis
        ax = self.figure.add_subplot(111)
        ax.set_aspect("auto", "box")

        # Axes names
        x_name = self.tr("Time (months)")
        y_name = self.tr("Contamination $(Bq.m^{-2})$")

        # Axes labels
        ax.set_xlabel(x_name)
        ax.set_ylabel(y_name)

        if self.dlg.cbox_y_scale.currentText() == "log":
            ax.set_yscale('log')

        # Set number of ticks on x-axis
        if len(y) > 10:
            ax.set_xticks([0, 1, len(y) // 4, len(y) // 2 - 1,
                           len(y) * 3 // 4 - 1, len(y) - 1])

        ax.tick_params(axis='x', rotation=90)

        # plot data
        ax.plot(y, '-', label=(self.tr("ID field: {ID}")).format(ID =
                                                                     pl_ID_text))

        # Legend position
        ax.legend(loc='best')

        plt.tight_layout()

        # Draw plot
        self.canvas.draw()

    def fillParams(self):
        "Fill parameters of the model to tables"

        self.fillGrowthModelTable()
        self.fillCN()
        self.fillCFactor()
        self.fillRadioTransferParams()
        self.fillSoilUnits()

        # Set enabled OK dialog button
        self.dlg.button_box.button(QDialogButtonBox.Ok).setEnabled(
            True)


    def fillSoilUnits(self):
        """Fill soil parameters (Soil hydrological category and
        K-factor to table tw_HPJ_params"""

        # Read unique values of HPJ (Main Soil Units) from data
        map_lyr = self.dlg.cbox_HPJ.currentLayer()
        field_name = self.dlg.cbox_HPJ_key.currentField()
        idx = map_lyr.fields().indexOf(field_name)

        # Extract unique vaues of HPJ from the layer
        hpj_set = map_lyr.uniqueValues(idx)
        hpj_list = list(sorted(hpj_set))

        # Read values from soil_hydr table
        hps_list = [self.soil_hydr["HPS"][i-1] for i in hpj_list]
        k_factor_list = [self.soil_hydr["K_factor"][i-1] for i in hpj_list]

        # Set No. of rows
        self.dlg.tw_HPJ_params.setRowCount(len(hpj_list))

        for i in range(len(hpj_list)):
            # Col. 0: HPJ
            self.dlg.tw_HPJ_params.setItem(i, 0, QTableWidgetItem(
                str(hpj_list[i])))
            # Col. 1: HPS
            self.dlg.tw_HPJ_params.setItem(i, 1, QTableWidgetItem(
                str(hps_list[i])))
            # Col. 2: K factor
            self.dlg.tw_HPJ_params.setItem(i, 2, QTableWidgetItem(
                str(k_factor_list[i])))

    def fillRadioTransferParams(self):
        """Fill Radiotransfer parameters for particular crops to
        tw_radio_coefs table"""

        # Get number of rows in tw_crops_orig table
        r_count = self.dlg.tw_crops_orig.rowCount()

        # Get current values from tw_crops_orig table
        crop_ind = [self.dlg.tw_crops_orig.cellWidget(i, 1).currentIndex()
                    for i in range(r_count)]

        # Variables lists
        crop_unique_ID = np.unique(crop_ind)
        crop_unique_names = [self.crops["crop"][i] for i in crop_unique_ID]

        if self.dlg.cbox_contaminant.currentIndex() == 0:   # Cs
            radio_coefs = [self.crops["R_transf_Cs"][i] for i in crop_unique_ID]
        else:       # Sr
            radio_coefs = [self.crops["R_transf_Sr"][i] for i in crop_unique_ID]

        # Set number of rows in table
        self.dlg.tw_radio_coefs.setRowCount(len(crop_unique_ID))

        # Set items
        for i in range(len(crop_unique_ID)):
            # col 1. ID
            self.dlg.tw_radio_coefs.setItem(i, 0, QTableWidgetItem(
                str(crop_unique_ID[i])))
            # col 2. crop names
            self.dlg.tw_radio_coefs.setItem(i, 1, QTableWidgetItem(
                str(crop_unique_names[i])))
            # col 3. Radiotransfer coef.
            self.dlg.tw_radio_coefs.setItem(i, 2, QTableWidgetItem(
                str(radio_coefs[i])))

    def fillCFactor(self):
        """Fill C factor values to tw_C_factor table"""

        # Get number of rows in tw_crops_orig table
        r_count = self.dlg.tw_crops_orig.rowCount()

        # Get current values from tw_crops_orig table
        crop_ind = [self.dlg.tw_crops_orig.cellWidget(i, 1).currentIndex()
                    for i in range(r_count)]

        # Variables lists
        crop_unique_ID = np.unique(crop_ind)
        crop_unique_names = [self.crops["crop"][i] for i in crop_unique_ID]
        c_factor = [self.crops["C_factor"][i] for i in crop_unique_ID]

        # Set number of rows in table
        self.dlg.tw_C_factor.setRowCount(len(crop_unique_ID))

        # Set items
        for i in range(len(crop_unique_ID)):
            # col 1. ID
            self.dlg.tw_C_factor.setItem(i, 0, QTableWidgetItem(
                str(crop_unique_ID[i])))
            # col 2. crop names
            self.dlg.tw_C_factor.setItem(i, 1, QTableWidgetItem(
                str(crop_unique_names[i])))
            # col 3. C factor
            self.dlg.tw_C_factor.setItem(i, 2, QTableWidgetItem(
                str(c_factor[i])))

    def fillCN(self):
        "Fill CN curve numbers to tw_CN table"

        # Get number of rows in tw_crops_orig table
        r_count = self.dlg.tw_crops_orig.rowCount()

        # Get current values from tw_crops_orig table
        crop_ind = [self.dlg.tw_crops_orig.cellWidget(i, 1).currentIndex()
                    for i in range(r_count)]

        # Variables lists
        crop_unique_ID = np.unique(crop_ind)
        crop_unique_names = [self.crops["crop"][i] for i in crop_unique_ID]
        cn_AG = [self.crops["CN_A_G"][i] for i in crop_unique_ID]
        cn_AB = [self.crops["CN_A_B"][i] for i in crop_unique_ID]
        cn_BG = [self.crops["CN_B_G"][i] for i in crop_unique_ID]
        cn_BB = [self.crops["CN_B_B"][i] for i in crop_unique_ID]
        cn_CG = [self.crops["CN_C_G"][i] for i in crop_unique_ID]
        cn_CB = [self.crops["CN_C_B"][i] for i in crop_unique_ID]
        cn_DG = [self.crops["CN_D_G"][i] for i in crop_unique_ID]
        cn_DB = [self.crops["CN_D_B"][i] for i in crop_unique_ID]

        # Set number of rows in table
        self.dlg.tw_CN.setRowCount(len(crop_unique_ID))

        # Set items
        for i in range(len(crop_unique_ID)):
            # col 1. ID
            self.dlg.tw_CN.setItem(i, 0, QTableWidgetItem(
                str(crop_unique_ID[i])))
            # col 2. crop names
            self.dlg.tw_CN.setItem(i, 1, QTableWidgetItem(
                str(crop_unique_names[i])))
            # col 3. CN AG
            self.dlg.tw_CN.setItem(i, 2, QTableWidgetItem(
                str(cn_AG[i])))
            # col 4. CN AB
            self.dlg.tw_CN.setItem(i, 3, QTableWidgetItem(
                str(cn_AB[i])))
            # col 5. CN BG
            self.dlg.tw_CN.setItem(i, 4, QTableWidgetItem(
                str(cn_BG[i])))
            # col 6. CN BB
            self.dlg.tw_CN.setItem(i, 5, QTableWidgetItem(
                str(cn_BB[i])))
            # col 7. CN CG
            self.dlg.tw_CN.setItem(i, 6, QTableWidgetItem(
                str(cn_CG[i])))
            # col 8. CN CB
            self.dlg.tw_CN.setItem(i, 7, QTableWidgetItem(
                str(cn_CB[i])))
            # col 9. CN DG
            self.dlg.tw_CN.setItem(i, 8, QTableWidgetItem(
                str(cn_DG[i])))
            # col 10. CN DB
            self.dlg.tw_CN.setItem(i, 9, QTableWidgetItem(
                str(cn_DB[i])))

    def fillGrowthModelTable(self):
        """Fill parameters of particular crops to the
        tw_growth_params table"""

        # Get number of rows in tw_crops_orig table
        r_count = self.dlg.tw_crops_orig.rowCount()

        # Get current values from tw_crops_orig table
        crop_ind = [self.dlg.tw_crops_orig.cellWidget(i,1).currentIndex()
                    for i in range(r_count)]

        # Variables lists
        crop_unique_ID = np.unique(crop_ind)
        crop_unique_names = [self.crops["crop"][i] for i in crop_unique_ID]
        crop_dw_max = [self.crops["dw_max"][i] for i in crop_unique_ID]
        crop_lai_max = [self.crops["LAI_max"][i] for i in
                        crop_unique_ID]
        crop_r_max = [self.crops["r_max"][i] for i in crop_unique_ID]
        crop_r_min = [self.crops["r_min"][i] for i in crop_unique_ID]

        # Set number of rows in table
        self.dlg.tw_growth_params.setRowCount(len(crop_unique_ID))
        # Set items
        for i in range(len(crop_unique_ID)):
            # col 1. ID
            self.dlg.tw_growth_params.setItem(i, 0, QTableWidgetItem(
                str(crop_unique_ID[i])))
            # col 2. crop names
            self.dlg.tw_growth_params.setItem(i, 1, QTableWidgetItem(
                str(crop_unique_names[i])))
            #col 3. Sowing date
            date_sow_in = datetime.date.fromisoformat(self.crops["sowing"][crop_unique_ID[i]])
            date_edit_sow = QDateEdit()
            date_edit_sow.setDisplayFormat("dd.MM")
            date_edit_sow.setDate(QDate(date_sow_in))
            date_edit_sow.setCalendarPopup(True)
            self.dlg.tw_growth_params.setCellWidget(i, 2, date_edit_sow)
            # col 4. harvest date
            date_harv_in = datetime.date.fromisoformat(self.crops["harvest"][crop_unique_ID[i]])
            date_edit_harv = QDateEdit()
            date_edit_harv.setDisplayFormat("dd.MM")
            date_edit_harv.setDate(QDate(date_harv_in))
            date_edit_harv.setCalendarPopup(True)
            self.dlg.tw_growth_params.setCellWidget(i, 3,
                                                    date_edit_harv)
            # col 5. Max dry mass
            self.dlg.tw_growth_params.setItem(i, 4, QTableWidgetItem(
                str(crop_dw_max[i])))
            # col 6. Max LAI
            self.dlg.tw_growth_params.setItem(i, 5, QTableWidgetItem(
                str(crop_lai_max[i])))
            # col 7. Max biomass moisture
            self.dlg.tw_growth_params.setItem(i, 6, QTableWidgetItem(
                str(crop_r_max[i])))
            # col 8. Min biomass moisture
            self.dlg.tw_growth_params.setItem(i, 7, QTableWidgetItem(
                str(crop_r_min[i])))
        # col 9. coef. m and col 10 coef. n
        self.calculateGowthCurveCoefs()

    def calculateGowthCurveCoefs(self):
        """Calculate default coefficients (slope and intercept of
        growth curves for the particular crops and add them to the
        tw_growth_params table"""

        # Get number of rows in the table
        r_count = self.dlg.tw_growth_params.rowCount()
        # Read dry mass values from the table
        dw_list = [float(self.dlg.tw_growth_params.item(i, 4).text())
                   for i in range(r_count)]

        # Calculate slopes and intercepts of growth models for crops
        # and set it to table
        for i in range(r_count):
            coef_m, coef_n = sl.calculateGrowthCoefs(dw_list[i])
            # col 9. coef. m
            self.dlg.tw_growth_params.setItem(i, 8, QTableWidgetItem(
                str(round(coef_m, 3))))
            # col 10. coef. n
            self.dlg.tw_growth_params.setItem(i, 9, QTableWidgetItem(
                str(round(coef_n, 3))))

    def setClimateTable(self):
        """Set soil saturation state in form of cboxes to table"""

        # Get row counts:
        row_count = self.dlg.tw_climate.rowCount()

        # Add cboxes to table
        for i in range(row_count):
            # create cboxes
            combo = QComboBox()
            combo.addItems(self.soil_sat.values())
            # add cboxes
            self.dlg.tw_climate.setCellWidget(i, 2, combo)
            # Set doublespinboxes for settings monthly mean temperature
            # and precipitation
            spin_temperature = QDoubleSpinBox()
            spin_temperature.setMinimum(-50.0)
            spin_precip = QDoubleSpinBox()
            self.dlg.tw_climate.setCellWidget(i, 0, spin_temperature)
            self.dlg.tw_climate.setCellWidget(i, 1, spin_precip)

    def tableRemoveRow(self, table):
        """Remove row from table"""

        # Get row counts:
        row_count = table.rowCount()
        table.setRowCount(row_count - 1)

    def meadowTableAddRow(self, table):
        """Add rows with meadows mowing and month of harvest to the
        table for the area of
        interest.

        :param table: Table of meadows mowing from UI (QTableWidget).
        """

        # Set column witdth
        table.setColumnWidth(0, 250)

        # Get row counts:
        row_count = table.rowCount()
        cuts_list = {0:self.tr("First mowing"),
                     1:self.tr("Second mowing"),
                     2:self.tr("Third mowing")}

        # Months list
        months = np.arange(1,13,1).astype(str)

        # Set new row
        if row_count < 3:
            table.setRowCount(row_count + 1)

        # Add cboxes and dateEdit boxes to tw_sowing table
        # create cboxes
        combo_crops = QComboBox()
        combo_crops.addItems(cuts_list.values())

        # Create date cboxes
        combo_har = QComboBox()
        combo_har.addItems(months)
        # add cboxes to table
        table.setCellWidget(row_count, 0, combo_crops)
        # add date edit widgets to table
        table.setCellWidget(row_count, 1, combo_har)

    def cropTableAddRow(self, table):
        """Add row with crops and terms of sowing and harvest to
        sowing procedure table for the area of interest.

        :param table: Table of crops rotation with sowing and harvest
            terms (QTableWidget).
        """

        # Set column witdth
        table.setColumnWidth(0, 250)

        # Get row counts:
        row_count = table.rowCount()
        crops_list = list(self.crops["crop"])

        # Months list
        months = np.arange(1,13,1).astype(str)

        # Set new row
        table.setRowCount(row_count + 1)

        # Add cboxes and dateEdit boxes to tw_sowing table
        # create cboxes
        combo = QComboBox()
        combo.addItems(crops_list)
        # Create date edit boxes
        combo_sow = QComboBox()
        combo_sow.addItems(months)
        combo_har = QComboBox()
        combo_har.addItems(months)
        # add cboxes to table
        table.setCellWidget(row_count, 0, combo)
        # add date edit widgets to table
        table.setCellWidget(row_count, 1, combo_sow)
        table.setCellWidget(row_count, 2, combo_har)

    def setOrigCropsToTable(self):
        """Set crops from crop field defined by user to table
        and select corresponding crops from list"""

        map_lyr = self.dlg.cbox_crop_lyr.currentLayer()
        fname = self.dlg.cbox_crop_lyr_key.currentField()
        idx = map_lyr.fields().indexOf(fname)
        values_set = map_lyr.uniqueValues(idx)
        crops_list = list(self.crops["crop"])

        # Fill first table
        if len(values_set) <= 100:
            self.dlg.tw_crops_orig.setRowCount(len(values_set))
            row = 0
            for i in values_set:
                self.dlg.tw_crops_orig.setItem(row, 0, QTableWidgetItem(
                    str(i)))
                row = row + 1

            # Add cboxes to second table
            for i in range(len(values_set)):
                # Create cbox
                combo = QComboBox()
                combo.addItems(crops_list)
                # add cbox to table
                self.dlg.tw_crops_orig.setCellWidget(i, 1, combo)
        else:
            self.iface.messageBar().pushMessage(self.tr("Error"),
                self.tr("Not possible to load data to the table. "
                        "The list of data is too long."), level=Qgis.Warning)

    def constants(self):
        """Some constants used in the program"""

        # Read crops to pd.DataFrame
        if self.locale == "cs":
            crops_params_table = os.path.join(self.plugin_dir,
                                              "params/crops_params_cs.csv")
        else:
            crops_params_table = os.path.join(self.plugin_dir,
                                              "params/crops_params_en.csv")

        self.crops = pd.read_csv(crops_params_table)

        # Read Main soil units (HPJ) and hydrological soil groups
        soil_hps_table = os.path.join(self.plugin_dir,
                                      "params/Soil_hydr_cat.csv")
        self.soil_hydr = pd.read_csv(soil_hps_table)

        # The state of soil saturation by soil water: good (Do) or
        # bad (Šp)
        self.soil_sat = {0:self.tr("Good"), 1:self.tr("Bad")}

    def setKeyField(self, comboBox_in, comboBox_out):
        """Set variables from the map_lyr.

        :param comboBox_in: Combo box (QgsMapLayerComboBox) with vector
            layer.
        :param comboBox_out: Fields of vector layer.
        """

        map_lyr = comboBox_in.currentLayer()
        comboBox_out.setLayer(map_lyr)

    def reset(self):
        """Reset all settings in the UI"""
        # TODO: je potreba prodiskutovat jestli jo nebo ne. Zatim ne

        # # Set zero
        # self.dlg.cbox_rad_depo.setCurrentIndex(0)
        # self.dlg.cbox_precip.setCurrentIndex(0)
        # self.dlg.cbox_dmt.setCurrentIndex(0)
        # self.dlg.cbox_HPJ.setCurrentIndex(0)
        # self.dlg.cbox_crop_lyr.setCurrentIndex(0)
        # self.dlg.tw_sowing.setRowCount(0)

        # Remove tmp folder
        shutil.rmtree(self.tmp_folder)

    def showInfo(self):
        """Create infobox with acknowledgement. The infobox is shown
        during the start of the plugin."""

        image_path = os.path.join(self.plugin_dir, "help", "source",
                                 "figs", "symbols", "MV_CR2.png")

        pixmap = QPixmap(image_path).scaledToHeight(128,
                                            Qt.SmoothTransformation)

        msgBox = QMessageBox()
        msgBox.setIconPixmap(pixmap)
        msgBox.setText(self.tr("The RadAgro software development was "
                               "supported by the Ministry of the "
                               "Interior of the Czech Republic "
                               "research project VI20172020098"))
        msgBox.setWindowTitle(self.tr("Welcome to RadAgro!"))
        msgBox.exec()

    def pluginHelp(self):
        """Open the help file."""

        help_file = os.path.join(self.plugin_dir, "help", "build",
                                 "html", "index.html")

        help_file_norm = os.path.normpath(help_file)

        try:
            if sys.platform != "win32":
                QDesktopServices.openUrl(QUrl(help_file_norm,
                                              QUrl.TolerantMode))
            else:
                print(help_file)
                print(help_file_norm)
                os.startfile(help_file_norm)

        except IOError:
            self.iface.messageBar().pushMessage(self.tr("Warning!"),
                    self.tr("Ooops, the Help is not available..."),
                                                level=Qgis.Warning, duration=5)

    def setCboxEmpty(self, comboBox):
        """Setting of empty value (text) in comboBoxes."""

        comboBox.setCurrentIndex(0)

    def loadResults(self):
        """Load calculated vector layer of radioactive deposition
        time development."""

        # Get path to output
        out_lyr_path = self.dlg.out_file.filePath()

        try:
            self.iface.addVectorLayer(out_lyr_path, "", "ogr")
            self.iface.messageBar().clearWidgets()

        except FileNotFoundError:
            self.iface.messageBar().pushMessage(self.tr("Warning!"),
                        self.tr("Ooops, the layer has not been "
                                "loaded..."),
                                                    level=Qgis.Warning,
                                                    duration=5)

    def startWorker(self):
        """Start threads with calculation process and with progress
        bar."""

        # create a new worker instance
        worker = Worker(lambda: self.getLyrPath(self.dlg.cbox_HPJ),
         self.su_field,
         lambda: self.getLyrPath(self.dlg.cbox_crop_lyr),
         self.loadRasters,
         self.createCropsInitDf,
         self.readGrowthModelParams,
         self.readTransferCoef,
         self.earlyStage,
         self.readCropsRotation,
         self.readMeadowsCut,
         self.createCropsRotationTS,
         self.createCropsHarvestTS,
         self.createDryMassTS,
         self.readKFactorTable,
         ru.fK,
         ru.fLS,
         self.readCFactorTable,
         self.readRFactorPercTable,
         self.calculateRadioactiveContamination,
         self.exportRadioCont2GeoPackage,
         self.ls_factor_m,
         self.ls_factor_n)

        # configure the QgsMessageBar
        messageBar = self.iface.messageBar().createMessage(
            self.tr("Calculation of radioactive deposition in "
                    "progress:"), )
        progressBar = QProgressBar()
        progressBar.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        progressBar.setMinimum(0)
        progressBar.setMaximum(100)
        cancelButton = QPushButton()
        cancelButton.setText(self.tr('Cancel'))
        cancelButton.clicked.connect(worker.kill)
        messageBar.layout().addWidget(progressBar)
        messageBar.layout().addWidget(cancelButton)
        self.iface.messageBar().pushWidget(messageBar, Qgis.Info)
        self.messageBar = messageBar

        # start the worker in a new thread
        thread = QThread()
        worker.moveToThread(thread)
        worker.finished.connect(self.workerFinished)
        worker.error.connect(self.workerError)
        worker.progress.connect(progressBar.setValue)
        worker.progress_t.connect(progressBar.setFormat)
        thread.started.connect(worker.run)
        thread.start()
        self.thread = thread
        self.worker = worker

    def workerFinished(self):
        """Activity after worker thread finishing."""

        # clean up the worker and thread
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()

        # The page with graph enabled
        self.dlg.tabWidget.setTabEnabled(2, True)

        # remove widget from message bar
        self.iface.messageBar().popWidget(self.messageBar)
        # Create finish message and load lyrs
        self.iface.messageBar().clearWidgets()
        widget = self.iface.messageBar().createMessage("Info", self.tr(
            "The calculation has been done. Do you want to load the "
            "radioactive contamination layer to QGIS?"))
        button = QPushButton(widget)
        button.setText(self.tr("Load results"))
        button.pressed.connect(self.loadResults)
        widget.layout().addWidget(button)
        self.iface.messageBar().pushWidget(widget, Qgis.Info)

    def workerError(self, exception_string):
        """Exceptins of worker thread running."""

        # TODO - překlad
        self.iface.messageBar().pushMessage(self.tr(
            "Something wrong happened!\n{ex_str}").format(
                ex_str=exception_string),
            level=Qgis.Critical, duration=3)


class Worker(QObject):
    """Example worker for calculating the total area of all features
    in a layer"""
    # Threading was done due to:
    # https://snorfalorpagus.net/blog/2013/12/07/multithreading-in
    # -qgis-python-plugins/

    def __init__(self,
                 suLyrPath,
                 su_field,
                 getCropsPath,
                 loadRasters,
                 createCropsDf,
                 readGrowthModel,
                 readTransfCoefs,
                 earlyStage,
                 readCropsRot,
                 readMeadows,
                 createCropsRot,
                 createCropsHarvest,
                 createDryMass,
                 readKFactor,
                 calcFK,
                 calcFLS,
                 readCTable,
                 readRTable,
                 calcRadioactiveCont,
                 exportRadCont,
                 ls_m,
                 ls_n):

        QThread.__init__(self)

        # Read variables - calculation process can be done with
        # RadAgro.resultsCalculate method without threading
        self.suLyrPath = suLyrPath
        self.su_field = su_field
        self.getCropsPath = getCropsPath
        self.loadRasters = loadRasters
        self.createCropsDf = createCropsDf
        self.readGrowthModel = readGrowthModel
        self.readTransfCoefs = readTransfCoefs
        self.earlyStage = earlyStage
        self.readCropsRot = readCropsRot
        self.readMeadows = readMeadows
        self.createCropsRot = createCropsRot
        self.createCropsHarvest = createCropsHarvest
        self.createDryMass = createDryMass
        self.readKFactor = readKFactor
        self.calcFK = calcFK
        self.calcFLS = calcFLS
        self.readCTable = readCTable
        self.readRTable = readRTable
        self.calcRadioactiveCont = calcRadioactiveCont
        self.exportRadCont = exportRadCont
        self.ls_factor_m = ls_m
        self.ls_factor_n = ls_n

        self.killed = False

    def run(self):
        """Running of worker thread - all calculations of the
        radioactivity contamination changes time series"""

        self.progress.emit(0)
        try:
            perc = 0
            self.progress_t.emit(self.tr("{pr} %: Loading "
                                         "input layers").format(
                pr=str(
                perc)))
            self.progress.emit(perc)
            su_lyr_path = self.suLyrPath()

            perc = 10
            self.progress_t.emit(self.tr("{pr} %: Loading "
                                         "input layers").format(pr=str(perc)))
            self.progress.emit(perc)
            crops_path = self.getCropsPath()

            perc = 15
            self.progress_t.emit(self.tr("{pr} %: Rasters "
                                         "transformation").format(pr=str(perc)))
            self.progress.emit(perc)
            depo_path, precip_path, dmt_path = self.loadRasters()

            perc = 20
            self.progress_t.emit(self.tr("{pr} %: Data "
                                         "preprocessing").format(pr=str(perc)))
            self.progress.emit(perc)
            df_crops_init = self.createCropsDf(crops_path)

            perc = 25
            self.progress.emit(perc)
            self.progress_t.emit(self.tr("{pr} %: Data "
                                         "preprocessing").format(pr=str(
                perc)))
            df_growth_model_params = self.readGrowthModel()

            perc = 30
            self.progress.emit(perc)
            self.progress_t.emit(self.tr("{pr} %: Data "
                                         "preprocessing").format(pr=str(
                perc)))
            df_transf_coefs = self.readTransfCoefs()

            perc = 35
            self.progress.emit(perc)
            self.progress_t.emit(self.tr("{pr} %: Calculation "
                                         "of early stage").format(
                pr=str(perc)))
            self.earlyStage(depo_path, precip_path, crops_path,
                            df_crops_init)

            perc = 40
            self.progress.emit(perc)
            self.progress_t.emit(self.tr("{pr} %: Crops "
                                         "rotation").format(pr=str(
                perc)))
            df_crops_rotation = self.readCropsRot()

            perc = 45
            self.progress.emit(perc)
            self.progress_t.emit(self.tr("{pr} %: Crops "
                                         "rotation").format(pr=str(
                perc)))
            df_meadows = self.readMeadows()

            perc = 50
            self.progress.emit(perc)
            self.progress_t.emit(self.tr("{pr} %: Crops "
                                         "rotation").format(pr=str(
                perc)))
            df_crops_rotation_all = self.createCropsRot(
                df_crops_init, df_crops_rotation, df_meadows)

            perc = 55
            self.progress.emit(perc)
            self.progress_t.emit(self.tr("{pr} %: Crops "
                                         "rotation").format(pr=str(
                perc)))
            df_crops_harvest = self.createCropsHarvest(
                df_crops_init, df_crops_rotation, df_meadows)

            perc = 60
            self.progress.emit(perc)
            self.progress_t.emit(self.tr("{pr} %: Crops "
                                         "rotation").format(pr=str(
                perc)))
            df_crops_dw_all = self.createDryMass(df_crops_init,
                                        df_growth_model_params,
                                        df_crops_rotation, df_meadows)

            perc = 65
            self.progress.emit(perc)
            self.progress_t.emit(self.tr("{pr} %: Erosion").format(
                pr=str(perc)))
            k_factor_tab = self.readKFactor()

            perc = 70
            self.progress.emit(perc)
            self.progress_t.emit(self.tr("{pr} %: Erosion").format(
                pr=str(perc)))
            k_factor = self.calcFK(su_lyr_path,
                                        self.su_field, k_factor_tab,
                                        crops_path)

            perc = 75
            self.progress.emit(perc)
            self.progress_t.emit(self.tr("{pr} %: Erosion").format(
                pr=str(perc)))
            ls_factor = self.calcFLS(dmt_path,
                                          crops_path,
                                          self.ls_factor_m,
                                          self.ls_factor_n)

            perc = 80
            self.progress.emit(perc)
            self.progress_t.emit(self.tr("{pr} %: Erosion").format(
                pr=str(perc)))
            c_factor_tab = self.readCTable()

            perc = 85
            self.progress.emit(perc)
            self.progress_t.emit(self.tr("{pr} %: Erosion").format(
                pr=str(perc)))
            r_perc = self.readRTable()

            perc = 90
            self.progress.emit(perc)
            self.progress_t.emit(self.tr("{pr} %: Calculation "
                                         "of contamination "
                                         "changes").format(pr=str(
                perc)))
            self.calcRadioactiveCont(df_transf_coefs,
                                     df_crops_rotation_all,
                                     df_crops_harvest,
                                     df_crops_dw_all, k_factor,
                                     ls_factor, c_factor_tab, r_perc)

            perc = 95
            self.progress.emit(perc)
            self.progress_t.emit(self.tr("{pr} %: Export of "
                                         "results").format(pr=str(
                perc)))
            self.exportRadCont()

        except Exception:
            # forward the exception upstream
            self.error.emit(traceback.format_exc())

        self.finished.emit(100)

    def kill(self):
        """Kill the working thread."""

        self.killed = True

    finished = QtCore.pyqtSignal(object)
    error = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(int)
    progress_t = QtCore.pyqtSignal(str)
