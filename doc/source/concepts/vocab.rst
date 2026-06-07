:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 08/04/2026



Vocabulaire
============

| :ref:`F <gloss-f>` | :ref:`G <gloss-g>` | :ref:`L <gloss-l>` | :ref:`R <gloss-r>` | :ref:`S <gloss-s>` | :ref:`T <gloss-t>` |



.. _gloss-f:

F
-

Footprint
    Voir xxx
       


.. _gloss-g:

G
-

Graphe
   voir réseau de mobilité

Grille de densité
   caractérise l’espace suivant le nombre distincts de traces brutes. On construit deux grilles de densité :


Grille de densité "géométrie" 
   caractérise une grille haute résolution G1 (typiquement < 5 m) supposée représenter le niveau de détail du chemin


Grille de densité de "contexte" 
   caractérise une grille basse résolution G2 (> 15 m) supposée représenter la densité locale de la trace.


Grille de contraste » local 
   caractérise K = G1/G2. L’idée c’est que si un pixel G1 est fort comparativement dans un pixel G2 de valeur faible, alors c’est un maximum local.


Grille binaire
   i.e. ou de présence-absence. Elle correspond à un seuillage des pixels avec K > n.



.. _gloss-l:

L
-
   

Ligne centrale
   A définir encore. La traduction officielle en français de la « center line » est « ligne médiane » calculée à partir de la road surface. Ce terme n’est pas pertinent car il laisse penser que c’est une médiane, alors que cela correspond plutôt à un milieu géométrique. On renomme donc cette ligne en « ligne centrale »



.. _gloss-r:

R
-

Réseau de mobilité (Graphe)
   Est network is defined by :
   - a topology graph G (V, E) : a set of vertex V and a set of edges E, E V x V non oriented
   - a geometry for each edge E defined as as sequence of vertics (x, y, z) and represents accurately the common path followed by all the individual sample trajectories (i.e. accurate aggregate trajectories


.. _gloss-s:

S
-

Squelette 
    Le « squelette » correspond à l’ensemble des lignes centrales. Par construction (triangulation de Delauney), les lignes centrales forment un réseau

Surface de circulation ou Surface fréquentée (Road surface)
   est la surface vectorielle qui représente les empreintes laissées par l’homme à la suite d’une opération de vectorisation de la grille binaire.


.. _gloss-t:

T
-

Trace
   La trace est définie par un ensemble de points ordonnés, chaque point étant caractérisé par une position (x, y) et un temps (timestamp) (Van Damme et al., 2024). C'est un résultat d'une procédure : soit d'une Observation par un Sensor, capteur gps porté par un objet mobile (Platform), soit d'un retraitement d'une trace brute, soit d'une simulation.

Trace médiane ou fusionnée
   La trace fusionnée est la meilleure représentation géométrique d’un ensemble de traces suivant exactement le même trajet, défini d un point d origine à une destination (Van Damme et al., 2024).

Traces accurate aggregated trajectory
   La trace fusionnée exacte est une trace fusionnée qui optimise un critère de qualité Q par rapport à la vérité terrain VT (Van Damme et al., 2024).

    
