# OutdoorFootprintNetworkPipeline (ONFP)

is an open source (MIT) Python library w
Source code for creating an outdoor activity footprint network from GNSS trajectories, representing the human footprint (e.g., hiking or running).





```mermaid
graph LR
A(Traces brutes) -- Découpage --> B(Traces découpées) 
B -- Ré-échantillonnées --> C(Traces échantionnées spatialement 1m)
C -- Calcul densité --> D(grille de densités, "contraste", Raster binaire)
D -- Center Line --> E(construction du squelette)
E -- Topologie --> F(réseau avec une topologie)
F -- Recalage --> G(topologie + traces associées)
B -- Recalage --> G
```



## Script *1_decoup_et_resample.py*: Découpage et ré-échantillonnage des traces en entrée
          
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


## 




# Environment Setup

## Requirements

OutdoorFootprintNetworkPipeline requires the following Python packages and Plugin QGIS:

- Tracklib
- GeoNetLib
- Plugin QGis "SciPy Filters"


The environment setup depends on your profile: development (if you need to modify Tracklib or Geonetlib), or user (if you just want to run the pipeline on a use case).


### Development Environment Setup


1. You need to install the following libraries:

- clone the Tracklib from github
- clone the GeoNetLib from github
- Plugin QGis "SciPy Filters"


2. Comme les scripts vont être exécutés dans QGis, il faut configuer à QGis ces deux librairies:

Cliquer dans la barre de menu sur Préférences >> Options >> Système >> 

Puis dans le bloc "Environnement", ajouter une variable personnalisée:

*Appliquer* : ajouter au début
*Variable*  : PYTHONPATH
*Valeur*    : /home/md_vandamme/7_LIB/tracklib:/home/md_vandamme/7_LIB/GeoNetLib



### "Just want to run the pipeline on a use case" Environment Setup

1.




## How to Run the Code


### Input

A GNSS trace dataset in CSV format is required.


### Execution

Run this source code in the QGIS Python console to display the created layers.

Execute MainWorkflow.py to start the creation scripts.



