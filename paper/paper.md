---
title: 'OFNP: a Python package for generating outdoor activity footprint networks from GNSS trajectories'
tags:
  - trajectory classification
  - mobility data
  - Python
  - machine learning
authors:
  - name: Marie-Dominique Van Damme
    orcid: 0000-0002-0007-5972
    equal-contrib: true
    corresponding: true 
    affiliation: 1 
  - name: Yann Méneroux
    orcid: 0000-0001-9126-7496
    equal-contrib: true 
    affiliation: 2,1
affiliations:
 - name: Univ Gustave Eiffel, IGN-ENSG, LASTIG, France
   index: 1
 - name: Institut national de l’information géographique et forestière, France 
   index: 2
date: 23 March 2026
bibliography: paper.bib

---

# Summary





# Statement of need





## Overview


* Calcul d’une carte de densité à partir des traces GNSS

* De la vectorisation on extrait une ligne centrée ≡ arc de la topologie. ([@Centerline2016])
* Attribue les points des traces brutes à chaque arc de la topologie
* Reconstruit les bons morceaux de traces candidats pour chaque arc de la topologie
* Agrégation des morceaux de traces
* Conflation des traces fusionnées afin d’obtenir un réseau de mobilité


![Galery of the pipeline.\label{fig:pipeline}](pipeline.png)





# Conclusions



# References
