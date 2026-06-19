:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 07/06/2026



Lire les rapports de traitement
================================

Objectif
^^^^^^^^^

Le pipeline se décompose en trois grandes parties regroupant plusieurs briques de traitement (voir workflow). Certaines briques produisent un rapport de traitement enregistré dans un fichier JSON, permettant de conserver des informations sur les traitements effectués.

Une grande partie de ces résultats est également reportés dans les journaux d'exécution (logs) du pipeline. Ils peuvent ainsi être consultés directement pendant l'exécution pour suivre le déroulement des traitements et analyser les résultats intermédiaires.


Registre des rapports de traitement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Le tableau suivant recense ces fichiers et précise, pour chacun d'eux, la brique responsable de leur création ainsi que la partie du pipeline concernée.

À l'exception des deux premiers fichiers, qui sont générés une seule fois avant le démarrage des itérations, l'ensemble des autres fichiers est produit à chaque itération du pipeline. Il existe donc une occurrence distincte de ces fichiers pour chacune des itérations exécutées.


+------------------+------------+-----------------------------------------------------------------------------------------+
| FICHIER          | COMPOSANT  | QUAND                                                                                   |
+==================+============+=========================================================================================+
| env.json         | --         | Au tout début du pipeline (première instruction)                                        |
+------------------+------------+-----------------------------------------------------------------------------------------+
| rawdata.json     | --         | Dans la préparation des données, juste avant la première itération.                     |
+------------------+------------+-----------------------------------------------------------------------------------------+
| image1.json      | IMAGE      | Produit lors des opérations de calcul matriciel du pipeline.                            |
+------------------+------------+-----------------------------------------------------------------------------------------+
| topology1.json   | TOPOLOGY   | Produit lors de la création du squelette simplifié et de sa topologie.                  |
+------------------+------------+-----------------------------------------------------------------------------------------+
| mapmatch1.json   | GEOMETRY   | Résultats issus des traitements de map-matching.                                        |
+------------------+------------+-----------------------------------------------------------------------------------------+
| candidate1.json  | GEOMETRY   | Produit lors de la création des segments candidats pour chaque arc de la topologie.     |
+------------------+------------+-----------------------------------------------------------------------------------------+
| aggregate1.json  | GEOMETRY   | Résultats issus de l'opération d'aggrégation des segments candidats des traces valides. |
+------------------+------------+-----------------------------------------------------------------------------------------+
| conflate1.json   | GEOMETRY   | Résultats issus de l'opération de conflation entre les fusions et le squelette.         |
+------------------+------------+-----------------------------------------------------------------------------------------+


Exemple
^^^^^^^^^

La fonction ``report_file`` permet la lecture d’un fichier de rapport de résultats. Elle prend en paramètre *RESPATH*, correspondant au répertoire de sortie défini dans le fichier de configuration.


.. code-block:: Python

   from footprint2graph import report_file

   report_file(RESPATH, 'env.json')



Résultat :
::
    
    =================================================================
                  	PIPELINE REPORT INFORMATION                    

	Map Matching 
	    Itération n° : 1
	    fin du traitement : 04/06/2026 16:30:51

	Search radius (m):                50

	Results
	--------------------------------------------------
	Map-matched points:               25488 ( 88.74 % )
	Off-track points:                 3234 ( 11.26 % )

	Quality
	--------------------------------------------------
	Root Mean Square Error (RMSE) :   3 m
	Maximal displacement :            8.83 m


