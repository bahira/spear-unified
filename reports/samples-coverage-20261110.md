# Plage d’apprentissage et extrapolation — 10 novembre 2026

## Changement unique

Le script de régression sur points présente désormais `training_domain`, `split_coverage` et `coverage_note`, en JSON et en Markdown. Pour chaque partition réellement fournie : plage min/max, nombre de points sous la borne d’apprentissage, au-dessus, total hors plage et indicateur `extrapolation`. La partition test optionnelle n’est pas inventée.

Ces informations sont calculées après l’ajustement, sans participation à la fitness, à la sélection ni aux baselines. Les métriques existantes ne changent pas. Une observation à la borne appartient à la plage ; seules les inégalités strictes comptent comme hors plage.

## Exemple vérifié, données synthétiques

Dans la démo existante, la plage d’apprentissage est `[-1.975, 1.9]`. Les points de validation sont dans cette plage ; un des 23 points de test, à environ `1.949565`, la dépasse. Le rapport d’erreur reste valide pour les points évalués, mais comporte donc une observation en extrapolation.

| Partition | Lignes | Plage x | Sous plage | Au-dessus | Hors plage |
|---|---:|---|---:|---:|---:|
| train | 32 | [-1.975, 1.9] | 0 | 0 | 0 |
| validation | 21 | [-1.9295238095238094, 1.8800000000000003] | 0 | 0 | 0 |
| test | 23 | [-1.8765217391304347, 1.9495652173913043] | 0 | 1 | 1 |

## Preuves

- Trois nouveaux tests d’intégration ont échoué avant changement, faute de champs de couverture.
- Cas synthétiques fournis : points mixtes en et hors plage, tous les points dans la plage et absence de test optionnel. Contrôle des comptes, du Markdown et de l’absence de promotion.
- `python -m unittest discover -s tests -v` : **22 tests passent en 1,223 s**.
- `node --disable-warning=MODULE_TYPELESS_PACKAGE_JSON --test tests/benchmark.test.mjs` : **3 tests passent**, processus 0,194 s.
- Syntaxe Node et `git diff --check` : propres.
- Trois paires avant/après en processus neufs : candidat et toutes les métriques de partitions identiques.
- Sonde complète : 0.959 s ; médianes subprocess 170.50 ms avant / 148.92 ms après. Écart bruité, aucune accélération revendiquée.

Les temps comprennent démarrage Node, vérification des sources, chargement, recherche et écriture des rapports. Copies temporaires et données synthétiques uniquement ; aucun rapport client ni chemin d’entrée privé publié. Données brutes : `reports/samples-coverage-20261110.json`.
Base : `2f6f7f7fa8dd9db2939c59d8b6c17a634217a318`, Python 3.12.14, Node v24.19.0.

## Limites et suite

Le contrôle concerne la plage d’une seule coordonnée x, pas une distribution statistique : être dans la plage ne garantit ni indépendance des données, ni validité métier, ni erreur uniforme. Un point hors plage n’est pas automatiquement rejeté ; ses métriques restent visibles et l’utilisateur doit qualifier la pertinence de l’extrapolation. Aucun seuil ni résultat scientifique ajouté.

La draft PR #10 est complétée sans fusion ; l’issue #8 reste ouverte jusqu’à qualification de données et partitions réelles. Pas de changement visuel, donc vérification de rendu sans objet. Triple Helix : priorité à une information manquante observable, tests avant/après, petit contrôle du coût et rétrospective sans métrique inventée.
