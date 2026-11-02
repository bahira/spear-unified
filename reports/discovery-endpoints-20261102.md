# Validation Discovery aux bornes — 2 novembre 2026

## Changement

Les 127 points intérieurs de validation sont conservés et complétés par les deux bornes exactes du domaine. Le candidat et sa recherche restent inchangés : ces 129 points ne participent ni à la fitness ni à la sélection. Le critère `accepted_on_probe` applique le budget demandé à l'erreur maximale de cette grille étendue. Le rapport expose `endpoints_included: true`.

## Faux positif reproduit avant correction

Configuration : `2*x+1`, domaine `[0,0.1]`, graine 42, 64 points d'apprentissage, population 32, 8 générations, tolérance `0.167`.

Le moteur propose la constante `1.032672`.

| Contrôle | Erreur absolue maximale | Décision |
|---|---:|---|
| Ancienne grille intérieure, 127 points | 0.166181272440945 | Accepté |
| Nouvelle grille, bornes incluses, 129 points | 0.167328000000000 | Rejeté |

Le test de régression a échoué sur le code initial (acceptation vraie), puis passe après correction. Un calcul Python indépendant de `2*x+1` confirme l'erreur aux bornes ; aucun texte de formule cible n'est exécuté en Python. Le registre n'est pas modifié.

## Vérifications et petit budget

- `python -m unittest discover -s tests -v` : 12 tests passent en 0,577 s.
- `node --disable-warning=MODULE_TYPELESS_PACKAGE_JSON --test tests/benchmark.test.mjs` : 3 tests passent, durée de processus 0,162 s.
- Cinq recherches reproductibles : mêmes arbres, 0.500 s au total.
- Médiane recherche et validation : 15.65 ms ; médiane subprocess complet : 98.67 ms.
- `git diff --check` : propre.

Preuves brutes et temps par passage : `reports/discovery-endpoints-20261102.json`. Source moteur inchangée et contrôlée : `dc74937e396a81e62853962ddd7f9c8c8d43cc7a`. Environnement de mesure : Python 3.12.14, Node v24.19.0, VM Linux de cette session. Checkout neuf depuis GitHub, branche dédiée ; anciens fichiers non publiés de la VM non utilisés.

## Limites et suite

C'est une correction de qualité de validation, pas une accélération de kernel ou la découverte d'une nouvelle loi. Vérifier une grille incluant les bornes ne certifie toujours pas l'intervalle continu. Aucune donnée métier n'a été utilisée. Les tolérances illustratives ne sont pas approuvées par un client. Pas de changement visuel : pas de capture nécessaire.

La PR reste draft sans fusion automatique et l'issue #3 reste ouverte : la validation applicative et les compromis précision/vitesse de bout en bout demandent d'autres mesures.

Triple Helix appliqué : priorité à un défaut reproductible, contre-exemple avant correction, vérifications par outils et rétrospective dans l'état persistant. Aucun seuil adaptatif ni pourcentage de convergence inventé.
