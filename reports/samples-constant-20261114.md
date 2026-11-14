# Référence constante — 14 novembre 2026

Ajout de la moyenne des y d’apprentissage comme référence constante (`constant_baseline`, kind `training_mean`). Les métriques n/MSE/RMSE/erreur absolue maximale sont calculées pour chaque partition et chaque groupe dans/hors plage, avec `null` pour un groupe vide. Cette référence est descriptive et ne participe pas à la recherche ni à la sélection.

Trois nouveaux tests échouaient avant ajout et passent après : moyenne et erreurs vérifiées analytiquement, indépendance vis-à-vis des coordonnées/valeurs hors apprentissage, reconstruction pondérée des erreurs de groupes et partitions absentes. Total : 28 tests Python en 2,283 s et 3 tests Node en 0,179 s. `git diff --check` passe.

Démo synthétique : moyenne 2,733126466998365 ; RMSE validation constante 2,07664, affine 2,07496, quadratique 0,005414, candidat 0,005645. Le GP bat la constante mais ne démontre toujours pas un avantage sur la référence quadratique. L’apprentissage porte sur [-1.975,1.9] ; un point du test dépasse cette plage, identifié séparément par les métriques de groupe.

Trois paires alternées avant/après : candidat et métriques préexistantes exactement inchangés. Médianes processus complet 168,57 ms avant et 148,57 ms après ; petit échantillon bruité, aucun gain revendiqué. Ces coûts incluent démarrage Node, vérification des sources, recherche et écriture des rapports, pas un benchmark du calcul de la formule. Temps de recherche séparés et données brutes : samples-constant-20261114.json.

Données uniquement synthétiques ; aucune validation client, causalité, nouvelle loi physique ou garantie continue. Aucun candidat promu. Aucun changement visuel ; vérification de rendu sans objet. Prochaine étape : jeu réel autorisé avec partitions et unités documentées ; issue #8 reste ouverte.
