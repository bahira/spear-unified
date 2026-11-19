# Qualification numérique du pont natif — 13 novembre 2026

Une seule amélioration : une sonde indépendante reproductible (`python scripts/check_native_precision.py`), intégrée aux tests. Backend, seuils et runtime inchangés. Taylor 7 classique, aucune découverte de loi.

4096 points uniformes avec graine 20261113, neuf valeurs autour de -1/0/1 (nextafter et -0), six valeurs hors domaine jusqu’au maximum double fini, chacun évalué avec tolérance zéro puis 3e-6 : 8222 évaluations. Erreur maximale 2.7308396425285153e-6 aux bornes et 2.7151859613994134e-6 sur le tirage aléatoire. Comptes de routage vérifiés ; entrées intactes ; signe de -0 préservé. Repli hors [-1,1] et tolérance zéro : égalité observée avec math.sin sur cette plateforme.

19 tests Python passent en 0,643 s, trois tests Node passent en 0,290 s. Aucune dépendance installée. Sonde de précision et test vérifient directement les sorties C, pas seulement le code source.

Petit benchmark existant relancé : construction 38,60 ms, ensemble 0,555 s. À 65536 doubles préconstruits, ratio libm C / mixte : 1,161 (0 % hors domaine), 1,099 (50 %), 1,012 (100 %). Le dernier cas n’utilise aucune approximation : sa variation ne constitue pas un gain algorithmique. Une seule exécution, sept répétitions, ordre alterné ; détails dans native-mixed-20261113.json.

Coûts inclus : validation finie, allocation de sortie, vues ctypes, appel C, contrôle de tolérance et consommation de sortie. Construction des entrées, conversion listes/JSON, démarrage processus et compilation exclus du temps d’appel ; compilation rapportée séparément. Aucun gain client ni sélection automatique revendiqué. Les sondes sont finies et synthétiques ; elles ne certifient pas une borne continue. L’accord exact avec libm dépend de la plateforme. Pas de modification visuelle : contrôle du rendu sans objet.

Suite : distribution applicative réelle autorisée et coût complet de conversion ; issue #4 laissée ouverte, intégration runtime non effectuée.
