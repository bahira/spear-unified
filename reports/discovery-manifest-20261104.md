# Manifestes obligatoires du chemin Python — 4 novembre 2026

## Défaut et reproduction

Le wrapper `spear.discovery.discover` parcourait uniquement `checksums.items()`. Un manifeste vide supprimait ainsi tous les contrôles ; l'absence de `math-utils.ts` masquait une dérive de ce helper. Des manifestes non objets provoquaient une erreur de type plutôt qu'un refus explicite de validation.

Les tests isolés reproduisent le passage vers le subprocess sans l'exécuter : un mock sentinelle interrompt toute tentative de lancement. Ils altèrent seulement des copies temporaires des fichiers vendor. Avant correction : les cas manifeste vide et helper omis atteignaient cette sentinelle ; les objets invalides donnaient AttributeError.

## Correction

Le chemin Python exige un objet JSON et une empreinte SHA-256 hexadécimale de 64 caractères pour chacun des deux noms fixes `engine.ts` et `math-utils.ts`. Il vérifie leurs octets avant de lancer Node ; aucune entrée supplémentaire du manifeste ne devient un chemin de fichier à suivre. Les erreurs de schéma sont des `ValueError` explicites.

Après une recherche réussie, `source_files_verified` et `source_file_sha256` indiquent les empreintes réellement vérifiées. La recherche, ses contraintes numériques, le domaine demandé et le seuil d'acceptation ne changent pas. Le protocole du holdout reste celui de cette branche : la draft PR #9 sur les bornes reste indépendante.

## Preuves et coût

- `python -m unittest discover -s tests -v` : **19 tests passent en 0,829 s**.
- `node --disable-warning=MODULE_TYPELESS_PACKAGE_JSON --test tests/benchmark.test.mjs` : **3 tests passent**, durée de processus 0,171 s.
- Quatre nouveaux tests couvrent manifeste vide, helper omis et modifié, manifeste non objet et empreintes mal formées ; aucun lancement Node n'est autorisé dans ces cas.
- Le test d'intégration réel existant contrôle les nouveaux champs de provenance pour un cas valide.
- `git diff --check` passe.
- Cinq paires de recherches avant/après : candidats, holdout et acceptation identiques. **1.113 s** au total ; médianes d'appel Python complet **111.92 ms avant / 107.59 ms après**.

Les temps incluent validation Python, hachage, démarrage Node, recherche, lecture JSON et métadonnées ; ce petit écart est bruité et ne démontre aucun gain. Données brutes dans `reports/discovery-manifest-20261104.json`. Base de comparaison : `3be3bcfcd6630026369e2a43323aaa35f4b5f8e4`, Python 3.12.14, Node v24.19.0.

## Limites, méthode et suite

Le manifeste local reste supposé fiable ; modifier à la fois le moteur et les empreintes contourne ce contrôle de dérive. Ce n'est ni une signature amont ni une sandbox. Aucune donnée client, loi physique ou accélération applicative n'est validée. Les copies temporaires et les rapports synthétiques n'exposent pas de données privées. Pas de modification visuelle : vérification de rendu sans objet.

Triple Helix appliqué : priorité à un seul défaut vérifiable, contre-exemple avant correction, contrôles et petit budget, état mis à jour en fin d'itération. Aucun seuil adapté ni métrique de convergence fabriquée. La correction complète la draft PR #10 sur sa branche dédiée ; l'issue #8 reste ouverte pour les données et validations métier.
