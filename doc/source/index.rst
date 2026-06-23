:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 08/04/2026


Footprint2graph’s documentation
================================

.. image:: https://img.shields.io/github/languages/top/umrlastig/footprint2graph
   :alt: GitHub top language
   :target: https://github.com/umrlastig/footprint2graph
.. image:: https://www.repostatus.org/badges/latest/wip.svg
   :alt: WIP – Initial development is in progress, but there has not yet been a stable
   :target: https://www.repostatus.org/#wip
.. image:: https://img.shields.io/badge/Licence-MIT-brightgreen.svg?style=flat
   :alt: Software License
   :target: https://github.com/umrlastig/footprint2graph/blob/main/LICENCE

.

**footprint2graph** is an open-source Python processing pipeline designed to transform  GNSS trajectories recorded during outdoor recreational activities into mobility networks. It builds a graph of commonly used paths, derived from sets of observed traces collected. The resulting dataset models, for example, the mobility networks of hikers or runners within a defined area and timeframe. In the graph, edge geometries correspond to path segments reconstructed from the input trajectories.

The pipeline consists of several components, including GNSS point map-matching onto a network, trajectory merging and grid-based processing, all implemented using the Tracklib Python library.


.. figure:: img/Footprint2graph.png
  :width: 400
  :align: center


  **Figure 1.** A hikers’ footprint (in red) is derived from heatmaps (number of GNSS trajectories), forming a new topology. This highlights that hikers do not always follow the official trail network (BDTOPO trails in white). The challenge lies in representing only the paths effectively used by practitioners.



History and acknowledgement
-----------------------------

*Footprint2graph-pipeline* was initiated in 2025 as a comprehensive Python framework that builds
upon components previously developed and metrologically analyzed within the *Tracklib* library,
both developed by LASTIG, Univ. Gustave Eiffel, Géodata Paris, IGN. While *Tracklib* focuses
on the manipulation of GNSS trajectories, *Footprint2graph-pipeline* provides a pipeline for
constructing topological networks from GNSS trajectories, which is its primary objective.
  
*Footprint2graph-pipeline* was developed as part of the `IntForOut research Project <https://www.umr-lastig.fr/intforout/>`_ (Multisource spatial data INTegration FOR the Monitoring of Ecosystems under the pressure of OUTdoor recreation)
and was supported by the ANR under grant agreement no. ANR-23-CE55-0003.

*Footprint2graph-pipeline* has been developed by two contributors who are also involved in
maintaining *Tracklib*. It is designed to be used within the IntForOut project (2024-2027)
to generate different graphs for various activities across diverse spatial and temporal scales.

We acknowledge Filip Todić for the GitHub repository `centerline <https://github.com/fitodic/centerline>`_, from which the code implementing a Voronoi-based centerline extraction algorithm has been used.


How to Cite Footprint2graph
-------------------------------------

To be completed




Table of Contents
------------------

.. toctree::
  :maxdepth: 1

  Installation <install>
  Examples <examples/index>
  How-to Guides <howto/index>
  Concepts <concepts/index>
  Reference <reference/index>

