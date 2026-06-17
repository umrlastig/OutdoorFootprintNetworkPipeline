:Author: Marie-Dominique Van Damme
:Version: 1.0
:License: --
:Date: 08/04/2026


End-to-End Examples
====================


À partir de trajectoires synthétiques
--------------------------------------

Cet exemple, décliné en une version *quickstart* et une version détaillée, offre une introduction rapide à **footprint2graph**. Il permet aux utilisateurs d’expérimenter la chaîne de traitement et de se familiariser avec ses principales étapes et paramètres. Il s’appuie sur la génération de trajectoires simulées à partir d’un réseau, ce qui facilite les tests dès lors qu’un réseau est disponible sous la forme d’un ensemble de géométries représentant les arêtes du graphe.


.. nbgallery::
    :name: quickstart-gallery
    :glob:

    Quickstart
    PedestrianGraphPlanDeLaLimace


Génération des jeux de données publiés
---------------------------------------

Ces deux exemples contiennent le code source qui a permis de générer deux jeux de données publiés dans l'entrepot de données 
`Recherche Data Gouv <https://entrepot.recherche.data.gouv.fr/dataverse/intforout>`_  et qui sont situés dans deux petites zones situées dans le Parc Régional des Bauges et dans la vallée de Chamonix. Ces deux exemples font partie d'un livrable du Work Package 2 du `projet de recherche IntForOut <https://www.umr-lastig.fr/intforout/>`_ .

Les données GNSS ont été produites et délivrées par la plateforme **Outdoorvision** (service fournissant des traces partagées volontairement par des utilisateurs lors de leurs activités de plein air), plateforme soutenue par le *Pôle Ressources National Sports de Nature* (**PRNSN**). Dans le cadre du projet de recherche IntForOut, les traces ont été extraites de la plateforme, après nettoyage, filtrage et anonymisation.


.. nbgallery::
    :name: intforout-gallery
    :glob:

    HikersFootprintBaugesArea


