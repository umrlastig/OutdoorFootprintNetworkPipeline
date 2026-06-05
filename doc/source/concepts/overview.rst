:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 08/04/2026


Pipeline overview
==================

Le pipeline est composé de 5 briques à exécuter une par une:

+------------------------+---------------------------------+--------------------+
|                        | DESCRIPTION                     | OUTPUT DIR         |
+========================+=================================+====================+
| Script 1               | filtre, decoup, resample        | decoup, resample   |
+------------------------+---------------------------------+--------------------+
| Script 2               | création et traitement images   | image, network     |
+------------------------+---------------------------------+--------------------+
| Script 3               | topologie                       | network            |
+------------------------+---------------------------------+--------------------+
| Script 4               | recalage, fusion et raccord     | mapmatch, geometry |
+------------------------+---------------------------------+--------------------+
| Script 5               | 2ème itération                  |                    |
+------------------------+---------------------------------+--------------------+



Les scripts se lancent dans une console Python. 


Préparation des traces brutes
Création des cartes de pratiques sportives et extrait du réseau
Calcul de la topologie du réseau
Calcul de la géométrie des arcs du réseau
Second pass


.. image:: ../img/pipeline.png
  :width: 1000
  :align: center






Paramètres à renseigner :
--------------------------

* Le répertoire qui contient les traces au format CSV (un fichier par trace)
    
        tracescsvpath = r'/home/md_vandamme/5_GPS/OV/BAUGES/run/'

* Le répertoire qui va contenir tous les résultats : 

        tracespath = r'/home/md_vandamme/4_RESEAU/ExampleRunning/traces/'. 

  Chaque script lit et enregistre (col 3) des résultats dans un répertoire ou plusieurs répertoires. 

* Limites de la zone d'étude sous forme de coordonnées des sommets des vertex d'un polygone:

  X = [945878, 956330, 955879, 954402, 952511, 950389, 948774, 945857, 945878]

  Y = [6516870, 6516805, 6508417, 6506849, 6506503, 6505649, 6504150, 6503762, 6516870]

* RESAMPLE_SIZE = 1

* NB_OBS_MIN    = 10 # nombre de points minimum pour une trace

* DIST_MAX_2OBS = 50 # si supérieur on coupe la trace. Par exemple : a stop can create a break in the trajectory







<br/>

Ci-dessous un détail de chaque brique: 



<br/>
<!-- ===================================================================================================== -->
<!-- ===================================================================================================== -->

## Script 1: *Préparation des traces brutes*

Ce script prend en entrée des traces brutes en entrée du pipeline. A la fin du script un nouveau jeu de traces est produit, extraites, découpées et sélectionnées si elle traverse une figure géométrique, résolues spatialement à 1 mètre.

=> produit un jeu de traces, résolues spatialement à 1 mètre, 
                    extraites (peut-être découpées) suivant une figure géométrique


Découpage et ré-échantillonnage des traces brutes





<br/>
<!-- ===================================================================================================== -->
<!-- ===================================================================================================== -->

## Script 2: *Création des cartes de pratiques sportives et extrait du réseau*


Calculs des cartes de densité, de contraste et binaire à partir des traces GNSS 

=> produit un jeu de traces résolues spatialement à 1 mètre


- De la vectorisation on extrait une ligne centrée ≡ arc de la topologie 

avec Filtre morphologique, Vectorisation, Squeletisation



   
   



<br/>
<!-- ===================================================================================================== -->
<!-- ===================================================================================================== -->

## Script 3: *Calcul de la topologie du réseau*




<br/>
<!-- ===================================================================================================== -->
<!-- ===================================================================================================== -->

## Script 4: *Calcul de la géométrie des arcs du réseau*








