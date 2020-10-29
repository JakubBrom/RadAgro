# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RadHydro
                                 A QGIS plugin
 QGIS plugin for temporal analysis of radioactivity contamination changes in field crops
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-10-23
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Dr. Jakub Brom, University of South Bohemia in České Budějovice, Faculty of Agriculture, Czech Republic
        email                : jbrom@zf.jcu.cz
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, \
    QCoreApplication, Qt, QUrl
from qgis.PyQt.QtGui import QIcon, QDesktopServices, QImage, QPixmap
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QComboBox, \
    QPushButton, QMessageBox

# Initialize Qt resources from file resources.py
from .resources import *

from qgis.core import Qgis, QgsMapLayerProxyModel

# Import the code for the dialog
from .RadHydro_dialog import RadHydroDialog
import sys
import urllib.request
import os.path


class RadHydro:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RadHydro_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&RadHydro for QGIS')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.pluginIsActive = False
        self.dlg = None

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
        return QCoreApplication.translate('RadHydro', message)


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

        icon_path = ':/plugins/RadHydro/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'RadHydro for QGIS'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if not self.pluginIsActive:
            self.pluginIsActive = True
            self.dlg = RadHydroDialog()

        # Help
        self.dlg.button_box.helpRequested.connect(self.pluginHelp)

        # Set initial index of cbox_precip as 0
        self.dlg.cbox_precip.setCurrentIndex(0)




    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&RadHydro for QGIS'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        # Reset settings of the UI
        self.reset()

        # print "** STARTING UrbanSARCA"
        self.showInfo()

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

        # Set fields from HPJ layer to fieldCbox
        self.dlg.cbox_HPJ.layerChanged.connect(lambda:
                                                    self.setKeyField(
                                                        self.dlg.cbox_HPJ, self.dlg.cbox_HPJ_key))





        # show the dialog
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def setKeyField(self, comboBox_in, comboBox_out):
        """Set variables from the map_lyr"""

        map_lyr = comboBox_in.currentLayer()
        comboBox_out.setLayer(map_lyr)



    def reset(self):
        """Reset all settings in the UI"""

        pass
        # TODO: je potreba prodiskutovat jestli jo nebo ne. Zatim ne

        # # Set zero
        # self.dlg.cbox_rad_depo.setCurrentIndex(0)
        # self.dlg.cbox_precip.setCurrentIndex(0)
        # self.dlg.cbox_dmt.setCurrentIndex(0)
        # self.dlg.cbox_HPJ.setCurrentIndex(0)
        # self.dlg.cbox_crop_lyr.setCurrentIndex(0)

    def showInfo(self):
        icon_path = 'https://upload.wikimedia.org/wikipedia/commons/7/79/MV_%C4%8CR.png'
        data = urllib.request.urlopen(icon_path).read()
        # TODO: import obrazku z lokalniho souboru --> nacitani z internetu
        #  je sileny...

        image = QImage()
        image.loadFromData(data)
        pixmap = QPixmap(image).scaledToHeight(128,
                                            Qt.SmoothTransformation)
        msgBox = QMessageBox()
        msgBox.setIconPixmap(pixmap)
        msgBox.setText(self.tr("Vývoj programu RadHydro for QGIS byl "
                               "podpořen z projektu Ministerstva "
                               "vnitra České republiky VI20172020098"))
        msgBox.setWindowTitle(self.tr("Poděkování"))
        msgBox.exec()

    def pluginHelp(self):
        """Open the help file.
        """
        help_file = os.path.join(self.plugin_dir, "help", "build",
                                 "html", "index.html")
        try:
            QDesktopServices.openUrl(QUrl(help_file))
        except IOError:
            self.iface.messageBar().pushMessage(self.tr("Help error"),
                    self.tr("Ooops, an error occured during help file"
                    " opening..."), level=Qgis.Warning, duration=5)

    def setCboxEmpty(self, comboBox):
        """Setting of empty value (text) in comboBoxes"""

        comboBox.setCurrentIndex(0)
