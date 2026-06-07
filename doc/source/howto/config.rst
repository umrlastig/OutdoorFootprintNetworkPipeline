:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 05/06/2026


Fichier de paramètres 
======================

Ce document décrit la structure et le rôle du fichier de configuration utilisé pour paramétrer l’exécution du pipeline.

Le fichier est écrit au format **YAML**, un format de configuration lisible permettant de structurer des données hiérarchiques sous forme de paires clé/valeur.

Un exemple de fichier de configuration est disponible dans le répertoire **data** de la bibliothèque *footprint2graph* sur GitHub, sous config_zone1.yml: https://github.com/umrlastig/footprint2graph/blob/main/data/config_zone1.yml.

Ce fichier est obligatoire pour l’exécution du pipeline footprint2graph. Il peut être enregistré à l’emplacement de votre choix.



1. Vue d’ensemble
^^^^^^^^^^^^^^^^^^^

Le fichier de paramètres est organisé en plusieurs sections :

- output : définition du chemin pour toutes les sorties données intermédiaires et données finales ;
- graph_construction : paramètres généraux liés à la définition d'une trace et ses échantillonnage ainsi que les résolutions spatiales des grilles de densité dans les traitements ;
- iterations : liste des paramètres utilisées pour les traitements itératifs.



2. Section "output"
^^^^^^^^^^^^^^^^^^^^

Cette section définit le chemin pour toutes les sorties données intermédiaires et données finales:

.. code-block:: yaml

   output:
     RESULT_PATH: /home/glagaffe/footprint2graphe/results/bauges2024/


*RESULT_PATH* : répertoire


Le répertoire de sortie est automatiquement nettoyé au démarrage du pipeline : tous les fichiers et sous-répertoires qu'il contient sont supprimés. Les répertoires et fichiers nécessaires sont ensuite recréés progressivement au cours de l'exécution.

À la fin de chaque étape du pipeline, les données produites sont enregistrées dans ce répertoire. Cette organisation permet :

- de consulter ou visualiser les résultats intermédiaires ;
- de relancer l'exécution à partir d'une étape spécifique ;
- d'inspecter les données générées par chaque brique de traitement ;
- de modifier, remplacer ou insérer de nouvelles briques dans le pipeline.



3. "Paramètres généraux"
^^^^^^^^^^^^^^^^^^^^^^^^^

Cette section regroupe les paramètres généraux liés à la définition des traces, à leur échantillonnage ainsi qu'aux résolutions spatiales des grilles de densité utilisées par les traitements. Ces paramètres sont appliqués de manière identique à toutes les itérations du pipeline.



3.1 Nombre d'itérations
""""""""""""""""""""""""

Le paramètre obligatoire, *NUM_ITERATIONS*, de type entier, indique le nombre d’itérations utilisées pour la construction du graphe dans le pipeline.

.. code-block:: yaml

   graph_construction:
     NUM_ITERATIONS: 1



3.2 Définition d'une trace
""""""""""""""""""""""""""""

.. code-block:: yaml

   graph_construction:
     NB_OBS_MIN: 10
     DIST_MAX_2OBS: 50


*NB_OBS_MIN* : nombre minimum d’observations pour conserver un segment de trace. Si un segment contient moins de ce nombre de points, il est ignoré.

*DIST_MAX_2OBS* : distance maximale (en mètres) entre deux observations consécutives. Si cette distance est dépassée, la trace est découpée.



3.3 Rééchantillonnage des traces
""""""""""""""""""""""""""""""""""

Pour des raisons de performance et de compatibilité, les traces sont rééchantillonnées :

.. code-block:: yaml

   graph_construction:
     RESAMPLE_SIZE_GRID: 1
     RESAMPLE_SIZE_FUSION: 5


*RESAMPLE_SIZE_GRID* : résolution utilisée pour les calculs matriciels.

*RESAMPLE_SIZE_FUSION* : résolution utilisée lors du recalage et de la fusion des données.



3.4 Résolution spatiale des grilles de densité
"""""""""""""""""""""""""""""""""""""""""""""""

.. code-block:: yaml

   graph_construction:
     G1_SIZE: 2
     G2_SIZE: 30

*G1_SIZE* : haute résolution (typiquement < 5 m) supposée représenter le niveau de détail du chemin

*G2_SIZE* : basse résolution (> 15 m) supposée représenter la densité locale (contexte spatial) de la trace.



4. Section "iterations"
^^^^^^^^^^^^^^^^^^^^^^^^

Cette section définit les différentes configurations (autant de fois que le nombre d'itérations déclaré) de traitement appliquées de manière itérative.

Chaque entrée correspond à un jeu de paramètres utilisé lors d’une exécution du pipeline.


.. code-block:: yaml

   iterations:
     - SEUIL_DENSITE: 25
       SEUIL_SURFACE: 1000

       CUT_FACTOR: 5
       INTERP_DIST: 5
       CLEAN_DIST: 0

       CURVE_HEIGHT: 25
       CURVE_WAVE_LENGTH: 5

       SEARCH: 50
       BUFFER: 20


4.1 Filtres dans les images
""""""""""""""""""""""""""""

*SEUIL_DENSITE* : seuil n utilisé pour construire la grille binaire à partir de la grille de contraste K=G1/G2. Cette grille met en évidence les zones où la densité observée dans une cellule de G1 est élevée relativement à la densité de son voisinage dans G2. Les pixels dont le contraste dépasse le seuil sont considérés comme des maxima locaux potentiels.


*SEUIL_SURFACE* : surface minimale requise pour la garder après l'opération de vectorisation (on ne garde pas les roads surfaces trop petites). L'unité est en mètre carré.



4.2 Calcul de la centerline
""""""""""""""""""""""""""""

*CUT_FACTOR* : facteur de coupure dans le filtre de fourrier

*INTERP_DIST* : interpolation distance (m)

*CLEAN_DIST*  : cleaning distance (m)



4.3 Construction de la topologie du squelette
"""""""""""""""""""""""""""""""""""""""""""""""

*CURVE_HEIGHT* : longueur maximale pour qu'un arc du squelette soit considéré comme une arrête terminale d'un sommet de virage.

*CURVEH_WAVE_LENGTH* : propagation en mètre pour confondre le point de courbure maximale avec le sommet d'une arête terminale



4.4 Recalage et Fusion
""""""""""""""""""""""""

*SEARCH* : distance maximale autour du squelette dans laquelle les observations GNSS sont recherchées comme candidats afin d'être recalées sur le réseau.

*BUFFER* : distance définissant la zone tampon autour des extrémités des arcs du squelette. Lorsqu'une trace traverse cette zone, elle est découpée afin de générer les segments candidats à la fusion.



5. Recommandations
^^^^^^^^^^^^^^^^^^^

Le pipeline est particulièrement sensible aux valeurs des paramètres. Il est recommandé de consulter la rubrique *Points d'attention* afin de comprendre leur influence et d'adapter leur configuration au contexte spatial et aux caractéristiques des données.

Veillez à conserver une cohérence entre les différents paramètres. Par exemple, le pas d'échantillonnage des traces doit être compatible avec les résolutions des grilles utilisées dans les traitements.

Si vous modifiez la valeur d'un paramètre après une exécution, consultez la rubrique *Reprise après interruption* pour éviter de relancer l'ensemble du pipeline lorsque cela n'est pas nécessaire.


