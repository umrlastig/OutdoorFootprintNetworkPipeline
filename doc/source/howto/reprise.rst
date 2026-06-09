:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 09/06/2026


Reprendre une exécution
========================

Ce guide explique comment reprendre l'exécution du pipeline à partir d'une étape spécifique du processus, après une interruption ou lorsqu'il est nécessaire de relancer seulement une partie du traitement.

L'organisation du workflow facilite cette reprise :

- les données produites sont enregistrées progressivement dans le répertoire RESULT_PATH ;
- l'ensemble des paramètres est centralisé dans un unique fichier de configuration, qui peut être modifié selon les besoins.

Les sections suivantes décrivent les différentes méthodes permettant de reprendre l'exécution du pipeline à l'étape souhaitée.

Seules les deux premières méthodes sont disponibles avec une installation standard de la bibliothèque. Les méthodes suivantes nécessitent une installation en mode édition (voir la section Installation).


Reprendre après le pré-traitement des traces
----------------------------------------------

Pour relancer les itérations du pipeline tout en conservant les résultats du pré-traitement (découpage des traces et ré-échantillonnage):

1. Vérifiez que les répertoires suivants existent dans ``RESULT_PATH`` et contiennent un ou plusieurs fichiers pour chaque trace d'entrée :

- decoup
- resample_fusion
- resample_grid


2. Désactivez la préparation de la collection de traces en commentant le code suivant :


.. code-block:: Python

   '''
   collection = load_raw_tracks_split(config['output']['RESULT_PATH'],
                                      tracespathsource, fmt, X, Y)
   '''


3. Passez *None* à la place de la collection de traces lors de l'exécution des itérations du pipeline :

.. code-block:: Python

   for idx in range(NBITER):
       iteration_index = int(idx) + 1

       # run pipeline for the ith iteration
       run_iteration(iteration_index, config, None)

Le pipeline reprendra alors les itérations en utilisant les traces pré-traitées déjà présentes dans RESULT_PATH.


4. Attention : les paramètres NB_OBS_MIN et DIST_MAX_2OBS (voir la section Préparer les données pour le pipeline) interviennent à la fois dans le pré-traitement des traces et dans le composant final GEOMETRY. Modifier leur valeur lors d'une reprise du pipeline peut entraîner des incohérences entre les données déjà produites et les traitements relancés. 



Exécuter une seule itération
-----------------------------

Si le pipeline est configuré pour exécuter plusieurs itérations, vous pouvez le limiter à une seule en réduisant l'intervalle de la fonction ``range`` ou en interrompant la boucle à l'aide d'une instruction ``break``.


.. code-block:: Python

   for idx in range(0, 1): # NBITER
       iteration_index = int(idx) + 1

       # run pipeline for the ith iteration
       run_iteration(iteration_index, config, None)

       break

