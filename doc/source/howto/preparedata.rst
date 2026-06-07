:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 08/04/2026


Préparer les données
=====================


Objectif
^^^^^^^^^

Cette étape a pour objectif de préparer les données avant leur traitement par le pipeline. Une phase de préparation est nécessaire afin de garantir que les données respectent le format et les contraintes attendus en entrée.

Les traces doivent notamment être :

1. chargées en mémoire,
2. associées à un identifiant unique,
3. et exprimées dans un système de projection locale (East, North, Up).

La suite de cette section décrit la procédure à suivre.

Les opérations de rééchantillonnage et de découpage des traces, en fonction de leur longueur et de leur résolution, sont quant à elles réalisées automatiquement au cours de l'exécution du pipeline.


Prérequis techniques 
^^^^^^^^^^^^^^^^^^^^^^

Les données doivent être chargées et regroupées dans une instance de la classe TrackCollection, fournie par la bibliothèque Tracklib, dont dépend footprint2graph. Cette collection constitue le format d'entrée attendu par le pipeline.

Les traces peuvent être importées directement depuis des fichiers CSV ou GPX. 

Pour les données au format GPKG, un exemple complet de préparation et d'import est disponible dans le script GpkgToCsv.py: https://github.com/umrlastig/footprint2graph/blob/main/footprint2graph/util/GpkgToCsv.py


1. Chargement des données
^^^^^^^^^^^^^^^^^^^^^^^^^^

La première étape consiste à charger les données dans une collection de traces compatible avec le pipeline. Dans les exemples présentés ci-dessous (formats CSV et GPX), chaque trace est enregistrée dans un fichier distinct.



Si les données proviennent de fichiers GPX
"""""""""""""""""""""""""""""""""""""""""""

Avant l'import des données, il est nécessaire de spécifier le format des horodatages à l'aide de la méthode ``setReadFormat`` de la classe ``ObsTime``. Cette étape permet à Tracklib d'interpréter correctement les dates et heures contenues dans les fichiers.

Il faut ensuite définir un objet ``TrackFormat`` décrivant la structure des données à importer. Dans l'exemple ci-dessous, les données sont lues depuis des fichiers GPX (``ext='GPX'``), projetées dans un système de coordonnées local ENU (*East, North, Up*) (``srid='ENU'``) et extraites depuis des éléments de type *track* du fichier GPX (``type='trk'``).

Les traces sont alors chargées dans ``collection``, une instance de ``TrackCollection`` qui constitue le format d'entrée attendu par le pipeline.


.. code-block:: Python

   import tracklib as tkl

   tkl.ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")

   path = r'/home/glagaffe/5_GPS/MOI/VINCENNES'
   fmt = tkl.TrackFormat({
        'ext': 'GPX', 
        'srid': 'ENU', 
        'type': 'trk'})
   collection = tkl.TrackReader.readFromFile(path, fmt)

   print (' Number of tracks:', collection.size())
   collection.plot()


Si les données proviennent de fichiers CSV
"""""""""""""""""""""""""""""""""""""""""""

Concernant les données stockées dans des fichiers CSV, la configuration de l'objet TrackFormat est plus détaillée que pour les fichiers GPX. Elle permet de décrire précisément la structure des données à importer.

Les principaux paramètres sont les suivants :

- **time_fmt** : format des horodatages utilisé pour interpréter les dates et heures contenues dans les fichiers ;
- **srid** : système de coordonnées des données. Par exemple, ENU (East, North, Up) pour une projection locale ou GEO pour des coordonnées géographiques (longitude, latitude, altitude) ;
- **id_E** : contient la coordonnée X dans le système ECEF, la longitude dans le système GEO ou la coordonnée Est dans le système ENU
-  **id_N** : contient la coordonnée Y dans le système ECEF, la latitude dans le système GEO ou la coordonnées Nord dans le système ENU
- **id_U** : coordonnée Z (ECEF) ou l'altitude (GEO/ENU).
- **id_T** : contient le timestamp (en seconde ou dans le format time_fmt)
- **separator** : caractère(s) utilisé(s) pour séparer les champs. Les valeurs prédéfinies sont la virgule (,), l'espace ( ) et le point-virgule (;) ;
- **header** : nombre de lignes d'en-tête à ignorer avant la lecture des données ;
- **cmt** : caractère indiquant qu'une ligne correspond à un commentaire et ne doit pas être prise en compte ;
- **read_all** : indique si les colonnes supplémentaires du fichier doivent être lues. Lorsqu'il est activé, ces colonnes sont importées sous forme d'analytical features associées aux observations.


L'exemple ci-dessous présente une configuration complète couramment utilisée.

.. code-block:: Python

   import tracklib as tkl

   path = r'/home/md_vandamme/5_GPS/OV/BAUGES/run/'
   fmt = tkl.TrackFormat({'ext': 'CSV',
                       'srid': 'GEO',
                       'id_E': 1, 'id_N': 0, 'id_U': 3, 'id_T': 2,
                       'time_fmt': '4Y-2M-2DT2h:2m:2sZ',
                       'separator': ';',
                       'header': 0,
                       'cmt': '#',
                       'read_all': True})
   collection = tkl.TrackReader.readFromFile(path, fmt)

   print (' Number of tracks:', collection.size())
   collection.plot()


2. Ajouter un identifiant à la collection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

De nombreux traitements du pipeline nécessitent de pouvoir identifier chaque trace de manière unique. Il est donc indispensable d'attribuer un identifiant à chaque trace de la collection.

Dans l'exemple ci-dessous, cet identifiant est généré à l'aide d'un compteur incrémental. La méthode ``createAnalyticalFeature`` est ensuite utilisée pour l'ajouter à chaque trace sous la forme d'une analytical feature.

**Le nom de cet attribut doit impérativement être** TID, car il est utilisé par plusieurs traitements du pipeline.


.. code-block:: Python

   cpt = 1
   for track in collection:
       newtrack.createAnalyticalFeature('TID', str(cpt))
       cpt += 1


3. Système de référence ENU
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Les observations GNSS doivent être exprimées dans un système de projection locale (East, North, Up).

Si elles sont définies dans un système de coordonnées géographiques (longitude, latitude, altitude), elles doivent être converties vers un système projeté.

La bibliothèque tracklib permet d’effectuer cette conversion, comme illustré dans l’exemple ci-dessous.


.. code-block:: Python

   for track in collection:
      # Transformation GEO coordinates to ENU
      track.toENUCoords()




