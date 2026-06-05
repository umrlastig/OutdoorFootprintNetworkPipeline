:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 08/04/2026


Installation
=============

*OFNP* is supported on Python versions 3.10+.



Dependencies
-------------

OutdoorFootprintNetworkPipeline requires the following Python packages:

* `tracklib <https://pypi.org/project/tracklib/>`_ - tracklib for the variety of tools, operators and functions to manipulate GPS trajectories.
* `matplotlib <https://pypi.org/project/matplotlib/>`_ - Used for colormaps and 2D plotting.
* osgeo : gdal, ogr, osr (pour la partie vectorisation)
* Shapely (centerline et smooth)
* Fiona, Rasterio, Geopandas

.. Environment Setup










.. ## "Just want to run the pipeline on a use case" Environment Setup
.. 
.. 1. Install tracklib
.. 
.. 
.. 2. Configuer dans QGis la librairie tracklib:
.. 
.. Cliquer dans la barre de menu sur Préférences >> Options >> Système >> 
.. 
.. Puis dans le bloc "Environnement", ajouter une variable personnalisée:
.. 
.. *Appliquer* : ajouter au début
.. *Variable*  : PYTHONPATH
.. *Valeur*    : /home/glagaffe/7_LIB/tracklib
.. 
.. 
.. 
.. ## How to Run the Code
.. 
.. 
.. 
.. ### Input
.. 
.. A GNSS trace dataset in CSV format is required.
.. 
.. 
.. ### Execution
.. 
.. Run this source code in the Python console. Execute MainWorkflow.py to start the creation scripts.





