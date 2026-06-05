:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 08/04/2026


Introduction
=============


.. list-table::
   :widths: 50 50

   * - .. figure:: ../img/identifier_oui.png
          :width: 60%

          Human outdoor activity footprint network

     - .. figure:: ../img/identifier_non.png
          :width: 100%

          Trajectories do not always form a path


The outdoor footprint network is defined by :

* a topology graph G (V, E) : a set of vertex V and a set of edges E, E ⊆ V x V non oriented
* a geometry for each edge E defined as as sequence of vertics (x, y, z) and represents accurately the common path followed by all the individual sample trajectories (i.e. accurate aggregate trajectories)


Soit un ensemble de trajectoires, où chaque trajectoire est définie comme un ensemble de n points ordonnés. On définit une trace agrégée, comme la meilleure représentation géométrique du jeu de trajectoires suivant exactement la même route partant d’une origine vers une destination.




.. list-table::
   :widths: 50 50

   * - .. figure:: ../img/input.png
          :width: 100%

          Raw GNSS trajectories
     - .. figure:: ../img/IT2.png
          :width: 100%

          Outdoor Footprint Network

The two figures above illustrate the pipeline input (left) and output (right).




