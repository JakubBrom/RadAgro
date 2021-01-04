RadAgro software was created as a QGIS Python plug-in. The reason for
this approach was the possibility to use a QGIS tools and simplicity
of installation for users. In this context usage QGIS as a platform
for RadAgro can increase the power of the software.

The SW RadAgro itself is a tool for prediction of a temporal
development of radioactive contamination of the area of interest.

RadAgro calculates a temporal changes of radioactivity on basis of
crops rotation (e.i. sowing procedure, agronomy), soil erosion and
radioactivity decay. The radioactivity contamination development
in particular fields and patches is predicted in early phase (approx.
48 hours or days) after radiation accident including possible effect
of countermeasures (removing plants/crops above-ground biomass) and
as well as in long term period. The step of the prediction is one month.


Program structure
-----------------

The RadAgro software has the following structure:

.. code-block:: html

   .
    ├── help
    │   ├── build
    │   ├── source
    │   ├── make.bat
    │   └── Makefile
    ├── i18n
    │   └── RadAgro_en.ts
    ├── modules
    │   ├── activity_decay.py
    │   ├── hydrIO.py
    │   ├── __init__.py
    │   ├── mdaylight.py
    │   ├── overlap_clip.py
    │   ├── SARCA_lib.py
    │   ├── sowing_proc.py
    │   ├── usle.py
    │   ├── waterflow.py
    │   └── zonal_stats.py
    ├── params
    │   ├── crops_params_cs.csv
    │   ├── crops_params_en.csv
    │   ├── IMPORTANT-READ.txt
    │   └── Soil_hydr_cat.csv
    ├── __init__.py
    ├── icon.png
    ├── LICENSE
    ├── metadata.txt
    ├── pylintrc
    ├── RadAgro_dialog_base.ui
    ├── RadAgro_dialog.py
    ├── RadAgro.py
    ├── README.md
    ├── resources.py
    └── resources.qrc

The functional overview and structure is described in technical
documentation of RadAgro. The main modules of the RadAgro are
described and documented here.


Folders
+++++++

* help: contains Sphinx source data and exported html documentation
* i18n: contains data for translation
* modules: contains python modules described below
* params: contains LUTs with parameters for crops growth
  model, hydrological model, erosion model and radiotransfer.


Files
+++++

The files included in the RadAgro folder are described below:

* icon.png: Icon
* LICENSE: Text of GNU-GPL v.3 license
* metadata.txt: Metadata of RadAgro which are needed for extension
  reading by QGIS. The file contains information about RadAgro.
* pylintrc: Configuration file
* RadAgro.py: The main python module providing UI communication and
  calculation
* RadAgro_dialog.py: Contains an information about reading UI from
  QT source
* RadAgro_dialog_base.ui: Source file of user interface. Qt5 is used.
* README.md: GitHub readme file
* resources.py: Module for icon configuration
* resources.qrc: Metadata for icon configuration


Module RadAgro
--------------
Module RadAgro is main module of the SW, containing all methods used
for connection and usage of user interface by users and furthermore
methods providing calculation of the radioactive contamination
temporal changes of the area of interest. The methods for
communication with user are also included in the module.

.. automodule:: RadAgro
    :members:


Module activity_decay
-----------------------
Module activity_decay contains a methods for calculation of
radioactivity decay of a radionuclide. The activity decay is
calculated in monthly step for particular radionuclide on basis of its
lambda parameters (or half life of decay).

.. automodule:: modules.activity_decay
    :members:


Module hydrIO
------------------
Module hydrIO contains methods for importing and exporting spatial
geo-data. Some methods are created just for RadAgro SW.

.. automodule:: modules.hydrIO
    :members:


Module SARCA_lib
-----------------

Module SARCA_lib is a module of RadAgro following from previous
software solution SARCA (Spatial Assessment of Radioactive Contamination
of Agricultural Crops) used for calculation of radionuclides
distribution within soil and agricultural crops during early stage
after radiation accident. Module SARCA_lib contains methods
for calculation of crop growth analysis and for calculation of
radioactive distribution in the crops.

.. automodule:: modules.SARCA_lib
    :members:


Module usle
-------------

Module usle contains methods used for calculation of Universal Soil
Loss Equation for particular fields and patches in the area of
interest. For more details see chapters in this docs.

.. automodule:: modules.usle
    :members:


Module waterflow
----------------
Methods included in module waterflow are dedicated for analysis of
hydrological features of the area of interest. The methods are used for
calculation of all the water flows in the landscape, i.e.
evapotranspiration (both potential and actual) and surface and
subsurface runoff. The hydrological model is based on CN method.
Calculation step is one month. Furthermore, the methods for
calculation of flow accumulation and flow accumulation probability
are included. For more details see chapters in this docs.

.. automodule:: modules.waterflow
    :members:


Module mdaylight
-----------------
Module mdaylight provides methods for calculation of day length and
monthly means of day length on basis of latitude and day/month number.

.. automodule:: modules.mdaylight
    :members:


Module sowing_proc
------------------
Module sowing_proc provides methods for crops rotation time series
creation for particular crops planted in the area of interest.

.. automodule:: modules.sowing_proc
    :members:


Module overlap_clip
-------------------
Module overlay_clip provides methods for unifying and reprojecting
different coordinate systems of rasters and furthermore method for
clipping of overlapping area of the rasters including their
resampling.

.. automodule:: modules.overlap_clip
    :members:

Parameter of crops and soil settings
-------------------------------------
Parameters of crop growth model, soil features and radiation transfer
constants are stored in the param folder. The content of the files in
the directory can be changed in the following way:

**crops_params_cs.csv or crops_params_en.csv** - the data in the rows
and columns can be changed. The columns and their names can't be
changed. The rows and their order can't be changed. New rows can be
added. The files contains following fields/columns:

    * crop: Crop name
    * sowing: Date of sowing of the crop
    * harvest: Date of harvesting the crop
    * dw_max: Maximal dry mass of the aboveground biomass :math:`(t.ha^{-1})`
    * LAI_max: Maximal Leaf Area Index of the crop
    * r_max: Maximal content of water in biomass (% of mass)
    * r_min: Minimal content of water in biomass (% of mass)
    * C_factor: Crop factor of USLE constants for particular crops
    * CN_x_x: CN numbers for a particular crops and hydrological main soil groups (A - D) and for actual hydrological state of the soils (ISP: G - good, B - bad)
    * R_transf_Cs: Constants of radioactive transfer from soil to crops for Caesium
    * R_transf_Sr: Constants of radioactive transfer from soil to crops for Stroncium


**Soil_hydr_cat.csv** - the csv file contains information about
various soils:

    * HPJ: Main Soil Unit (from 1 to 78)
    * HPS: Main hydrological group of soil
    * K_factor: K factor constants of USLE for particular soils

All the data described above can be changed in RadAgro UI before the
calculation.