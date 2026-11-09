# Validation entre les points — 9 novembre 2026

## Contre-exemple reproduit

La grille de la draft PR #9 contenait 127 points intérieurs et les deux bornes, mais pouvait ignorer une variation très étroite entre deux points. Une cible synthétique est construite exprès au milieu d'un tel intervalle :

`exp(-1000000*(x-0.0042807559055118016)*(x-0.0042807559055118016))` sur `[-1,1]`, graine 42, tolérance `1e-4`, 64 points d'apprentissage, population 32, 8 générations.

Le moteur produit une expression équivalente à zéro. Sur les 129 anciens points, l'erreur maximale vaut environ 1,93e-22 ; le candidat est accepté. Au centre du pic, le calcul indépendant Python donne `exp(0)=1`, et le candidat vaut zéro : erreur réelle au point témoin égale à 1. Le test de régression échoue avant correction sur l'acceptation indue.

## Correction unique

Conserver les 129 points de base, ajouter les 128 milieux des intervalles adjacents. Les 257 évaluations restent hors de la fitness et de la sélection ; le moteur, la graine et les seuils ne changent pas. La même formule candidate est maintenant rejetée avec erreur maximale 1. Le rapport expose `midpoints_included`, `base_rows` et `midpoint_rows` en plus de `endpoints_included`.

Le contre-exemple des bornes et le contrôle indépendant x² restent testés. Le registre reste intact. Aucun point de validation n'est ajouté aux données d'apprentissage.

## Vérifications

- `python -m unittest discover -s tests -v` : **13 tests passent en 0,648 s**.
- `node --disable-warning=MODULE_TYPELESS_PACKAGE_JSON --test tests/benchmark.test.mjs` : **3 tests passent**, processus 0,187 s.
- Test du pic : échec observé avant, succès après ; son oracle indépendant porte sur le point témoin, pas sur le domaine entier.
- Trois paires de recherches en processus Node neufs, ordre alterné : **même candidat dans chaque paire**, accepté avant, rejeté après.
- Temps total de la sonde : **0.647 s**. Médianes subprocess complet : **105.60 ms avant / 108.26 ms après**.
- `git diff --check` : propre.

Ces temps comprennent démarrage Node, recherche et validation ; le hachage Python est hors du champ subprocess. Petite sonde bruitée sur VM, aucun gain de kernel revendiqué. Preuves brutes : `reports/discovery-midpoints-20261109.json`. Base : `d7d6800ca4ff4802afc9084c348c25f593616680`, Python 3.12.14, Node v24.19.0.

## Limites et suite

Ce raffinement fixe n'est ni une recherche adaptative ni une certification sur le continu : d'autres pics peuvent rester entre les nouveaux points. Il s'agit d'un contre-exemple synthétique intentionnel, sans données client ni nouvelle loi. Dans un intervalle extrêmement étroit en précision flottante, des milieux peuvent s'arrondir sur une extrémité : `rows` compte les évaluations, pas une garantie de coordonnées distinctes.

Prochaine étape à qualifier : points de validation supplémentaires ou contrôle analytique de régularité pour un domaine réel, avec coût et hypothèses explicites. L'issue #3 reste ouverte ; la draft PR #9 est complétée, sans fusion. Les PR #10 et #11 restent indépendantes.

Triple Helix : priorité à un défaut reproductible, contre-exemple, vérification par outils et rétrospective enregistrée sans métriques inventées ni adaptation des seuils. Pas de modification visuelle : contrôle du rendu sans objet.
