:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 08/04/2026


Pipeline overview
==================

.. Approche itérative

TODO



Première itération & Principe
------------------------------

.. Déroulement d'une itération du pipeline
.. Première itération : principe de fonctionnement


The pipeline consists of several components.

(1) First, GNSS trajectories are segmented and resampled to obtain homogeneous trajectories with respect to spatial and temporal resolution.
(2) Next, a synthetic representation of trajectories is generated through a grid-based processing approach, producing a heat map that highlights both major routes and secondary paths.
(3) This raster representation is then transformed into a vector skeleton, i.e., a graph whose edges represent the central axes of the identified movement corridors, using skeletonization operations.
(4) For each edge of the skeleton, the associated GNSS points are identified through map-matching operations. These points are subsequently grouped into trajectory segments, providing for each edge a set of individual traces to be compared and merged.
(5) The segments associated with a given edge are then merged in order to reconstruct as accurately as possible the common path followed by the different individual trajectories.
(6) Finally, a geometric adjustment step ensures the continuity of the reconstructed segments while preserving the topology of the skeleton, thereby producing the final mobility network.


.. figure:: ../img/workflow.png
  :width: 1000
  :align: center

  **Figure 1.** À partir des traces GNSS brutes, une carte de densité est construite afin d'extraire un squelette central servant de référence topologique. Les traces sont ensuite découpées en segments candidats à la fusion, regroupés pour calculer des trajectoires médianes, puis assemblées pour produire le réseau de mobilité final.


Les différentes étapes de l'algorithme, décrites après, peuvent être résumées ainsi:

0. Préparation des traces brutes
1. Calcul de cartes de densité à partir des traces GNSS
2. De la vectorisation, on extrait une ligne centrée ≡ arc de la topologie.
3. Attributione des points des traces brutes à chaque arc de la topologie
4. Construction de bons morceaux de traces candidats pour chaque arc de la topologie puis agrégation des morceaux de traces
5. Conflation des traces fusionnées afin d’obtenir un réseau de mobilit





  
*Préparation des traces brutes*
"""""""""""""""""""""""""""""""""

Ce script prend en entrée des traces brutes en entrée du pipeline. A la fin du script un nouveau jeu de traces est produit, extraites, découpées et sélectionnées si elle traverse une figure géométrique, résolues spatialement à 1 mètre.

=> produit un jeu de traces, résolues spatialement à 1 mètre, 
                    extraites (peut-être découpées) suivant une figure géométrique


Découpage et ré-échantillonnage des traces brutes




*Calcul d’une carte de densité à partir des traces GNSS*
""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Calculs des cartes de densité, de contraste et binaire à partir des traces GNSS 

=> produit un jeu de traces résolues spatialement à 1 mètre


- De la vectorisation on extrait une ligne centrée ≡ arc de la topologie 

avec Filtre morphologique, Vectorisation, Squeletisation



*Calcul de la topologie du réseau*
""""""""""""""""""""""""""""""""""""



*Calcul de la géométrie des arcs du réseau*
""""""""""""""""""""""""""""""""""""""""""""



*Conflation des traces fusionnées*
"""""""""""""""""""""""""""""""""""

Correction élastique de la géométrie du réseau



Itérations et embranchements
------------------------------

