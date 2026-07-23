# Footprint2Graph

<p align="center">
<table style="border:none;border:0;width:60%"><tr>
  <td align="center"><img width="800px" src="https://github.com/umrlastig/footprint2graph/blob/main/doc/source/img/footprint2graph.png" /></td>
</tr></table>
</p>


[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![Documentation Status](https://readthedocs.org/projects/footprint2graph/badge/?version=latest)](https://footprint2graph.readthedocs.io/en/latest/?badge=latest)
[![Software License](https://img.shields.io/badge/Licence-MIT-blue.svg?style=flat)](https://github.com/umrlastig/footprint2graph/blob/main/LICENCE)
[![Footprint2graph build & test](https://github.com/umrlastig/footprint2graph/actions/workflows/pipeline.yml/badge.svg)](https://github.com/umrlastig/footprint2graph/actions/workflows/pipeline.yml)
[![codecov](https://codecov.io/gh/umrlastig/footprint2graph/branch/main/graph/badge.svg?token=pHLaV21j2O)](https://codecov.io/gh/umrlastig/footprint2graph)

[![Supported Python Versions](https://img.shields.io/pypi/pyversions/footprint2graph.svg)](https://www.python.org/downloads/)
[![PyPI Version](https://img.shields.io/pypi/v/footprint2graph.svg)](https://pypi.python.org/pypi/footprint2graph/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/footprint2graph?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/footprint2graph)


Footprint2graph is an open-source Python processing pipeline (MIT license) for generating mobility networks from GNSS trajectories recorded during outdoor recreational activities. The output dataset representing, for example, hikers’ or runners’ network within a defined spatial and temporal extent.

The pipeline consists of several components, including GNSS point map-matching onto a network, trajectory merging and grid-based processing, all implemented using the Tracklib Python library.


## Documentation

The online documentation is available at **[ReadTheDocs](https://footprint2graph.readthedocs.io)**

Specifically, the documentation includes end-to-end example:
- **with a set of simulated trajectories generated from a network** : [quickstart example](https://footprint2graph.readthedocs.io/en/latest/examples/index.html)


## Citation

If you use footprint2Graph, please cite the following references:

<div style="background-color:rgba(200, 200, 200, 0.0470588); text-align:left; vertical-align: middle; padding:10px;">
Marie-Dominique van Damme, Yann Méneroux. footprint2graph: An Open-Source Python Pipeline for Generating Mobility Networks from GNSS Trajectories. 2026. [HAL Id](https://hal.science/hal-05665743v1)
</div>


```bibtex
@softwareversion{vandamme:hal-05665743v1,
  TITLE = {{footprint2graph: An Open-Source Python Pipeline for Generating Mobility Networks from GNSS Trajectories}},
  AUTHOR = {van Damme, Marie-Dominique and M{\'e}neroux, Yann},
  URL = {https://hal.science/hal-05665743},
  NOTE = {},
  PUBLISHER = {{Zenodo}},
  INSTITUTION = {{Institut National de l'Information G{\'e}ographique et Foresti{\`e}re}},
  YEAR = {2026},
  MONTH = Jun,
  DOI = {10.5281/zenodo.20800149},
  VERSION = {v1.1.1},
  REPOSITORY = {https://github.com/umrlastig/footprint2graph},
  LICENSE = {MIT License},
  KEYWORDS = {Spatial graph ; Trajectory ; GNSS ; human mobility},
  FILE = {https://hal.science/hal-05665743v1/file/footprint2graph-1.1.1.tar.gz},
  HAL_ID = {hal-05665743},
  HAL_VERSION = {v1},
}
```


## Acknowledgments

This framework was developed as part of the [IntForOut research Project](https://www.umr-lastig.fr/intforout/) (Multisource spatial data INTegration FOR the Monitoring of Ecosystems under the pressure of OUTdoor recreation) and was supported by the ANR under grant agreement no. ANR-23-CE55-0003.  


We acknowledge Filip Todić for the GitHub repository (https://github.com/fitodic/centerline), from which the code implementing a Voronoi-based centerline extraction algorithm has been used.


## Development & Contributions

* Institute: LASTIG, Univ Gustave Eiffel, Géodata Paris, IGN
* License: MIT license
* Authors:
  - Marie-Dominique Van Damme
  - Yann Méneroux







