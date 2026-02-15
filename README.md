# OutdoorFootprintNetworkPipeline (ONFP)

OFNP is an open-source Python processing pipeline (MIT license) for generating outdoor activity footprint networks from GNSS trajectories, representing, for example, hikers’ or runners’ footprints within a defined spatial and temporal extent. The pipeline consists of several components, including GNSS point map-matching onto a network and trajectory merging, both implemented using the Tracklib Python library.

The outdoor footprint network is defined by :

* a topology graph G (V, E) : a set of vertex V and a set of edges E, E ⊆ V x V non oriented
* a geometry for each edge E defined as as sequence of vertics (x, y, z) and represents accurately the common path followed by all the individual sample trajectories (i.e. accurate aggregate trajectories)


The two figures below illustrate the inputs and outputs of the pipeline.

<p align="center">
<table style="border:none;border:0;width:60%"><tr>
  <td align="center" style="width:30%">
    <img width="200px" src="https://github.com/IntForOut/HikersFootprint/blob/main/img/input.png" />
    <label>Raw GNSS trajectories</label>
  </td>
  <td style="padding:16px;">
    <img width="200px" src="https://github.com/IntForOut/HikersFootprint/blob/main/img/output.png" />
    <label>Outdoor Footprint Network</label>
  </td>
</tr></table>
</p>


> README Contents
> - [Pipeline Overview](#pipeline-overview)
>     * [Découpage et ré-échantillonnage des traces brutes](#script-1_decoup_et_resamplepy-découpage-et-ré-échantillonnage-des-traces-en-entrée)
>     * [Calculs des cartes de densité, de contraste et binaire](#script-2_calculs_des_cartes_de_densité_de_contraste_et_binaire)
> - [Environment Setup](#environment-setup)
>     * Requirements
>     * Environment Setup
>     * How to Run the Code

<br/>

# Pipeline Overview


|                |ASCII                          |OUTPUT DIR                   |
|----------------|-------------------------------|-----------------------------|
|Script 1        |                               |decoup and resample          |
|Script 2        |                               |densite                      |
|Script 3        |                               |network                      |


Chaque script enregistre des résultats dans un répertoire (colonne 3).


<br/>

<!-- ===================================================================================================== -->

## Script 1 *Découpage et ré-échantillonnage des traces brutes*

        
=> produit un jeu de traces, résolues spatialement à 1 mètre, 
                    extraites (peut-être découpées) suivant une figure géométrique

Le script peut être lancer sans QGIS, dans ce cas il faut commenter 


Paramètres à renseigner :
--------------------------

* RESAMPLE_SIZE = 1

* NB_OBS_MIN    = 10 # nombre de points minimum pour une trace

* DIST_MAX_2OBS = 50 # si supérieur on coupe la trace. Par exemple : a stop can create a break in the trajectory

* tracescsvpath = r'/home/md_vandamme/5_GPS/OV/BAUGES/run/'

* Limites de la zone d'étude sous forme de coordonnées des sommets des vertex :

X = [945878, 956330, 955879, 954402, 952511, 950389, 948774, 945857, 945878]
Y = [6516870, 6516805, 6508417, 6506849, 6506503, 6505649, 6504150, 6503762, 6516870]

* Le répertoire qui va contenir les nouvelles traces : découpées et ré-échantillonnées 

Il faut créer le répertoire avant de lancer le script.

tracespath = r'/home/md_vandamme/4_RESEAU/ExampleRunning/traces/'


En sortie :


<br/>

<!-- ===================================================================================================== -->

## Script 2 *Calculs des cartes de densité, de contraste et binaire*


=> produit un jeu de traces résolues spatialement à 1 mètre







# Environment Setup

## Requirements

OutdoorFootprintNetworkPipeline requires the following Python packages and Plugin QGIS:

- Tracklib
- GeoNetLib
- Plugin QGis "SciPy Filters"


## Environment Setup 

The environment setup depends on your profile: 

- development : in case you need to modify either the Tracklib or Geonetlib Python library , 
- or user (if you just want to run the pipeline on a use case).


### "May be to fix bug in tracklib and geonetlib" Environment Setup 

1. You need to install the following libraries:

- clone the Tracklib from github
- clone the GeoNetLib from github
- Plugin QGis "SciPy Filters"


2. Comme les scripts vont être exécutés dans QGis, il faut configuer à QGis ces deux librairies:

Cliquer dans la barre de menu sur Préférences >> Options >> Système >> 

Puis dans le bloc "Environnement", ajouter une variable personnalisée:

*Appliquer* : ajouter au début
*Variable*  : PYTHONPATH
*Valeur*    : /home/glagaffe/7_LIB/tracklib:/home/glagaffe/7_LIB/GeoNetLib



### "Just want to run the pipeline on a use case" Environment Setup

1.




## How to Run the Code


### Input

A GNSS trace dataset in CSV format is required.


### Execution

Run this source code in the QGIS Python console to display the created layers.

Execute MainWorkflow.py to start the creation scripts.



