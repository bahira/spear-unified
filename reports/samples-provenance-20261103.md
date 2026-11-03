# Provenance du moteur de régression sur observations — 3 novembre 2026

## Défaut reproduit

`scripts/discover_samples.mjs` déclarait la révision Superspear de `source.json` sans contrôler les empreintes des fichiers exécutés. Une simple modification de `math-utils.ts` produisait encore un rapport de succès ; un `throw` ajouté à `engine.ts` s'exécutait avant tout contrôle.

Les nouveaux tests ont d'abord échoué sur le code de base : deux échecs et une erreur pour le champ de vérification absent. Les sondes utilisent exclusivement des copies temporaires du moteur et des données synthétiques ; aucun fichier vendor réel ni rapport historique n'est modifié.

## Correction unique

- Lire le manifeste local puis exiger une empreinte SHA-256 valide pour `engine.ts` et `math-utils.ts`.
- Comparer les octets réels aux empreintes avant tout chargement du moteur.
- Charger ensuite le moteur par `await import(...)` : un import statique aurait déjà exécuté le code avant le contrôle.
- Refuser une dérive ou une empreinte obligatoire absente avant recherche et écriture de rapport.
- Exposer `source_files_verified: true` et `source_file_sha256` dans les rapports réussis.

L'algorithme, les splits, les seuils et les baselines restent inchangés. `search_ms` garde son périmètre ; `total_ms` inclut désormais aussi la vérification et le chargement dynamique situés après le départ du chronomètre. Le démarrage du processus reste à mesurer à l'extérieur.

## Vérifications

- `python -m unittest discover -s tests -v` : **15 tests passent en 0,747 s**, dont quatre tests de provenance.
- `node --disable-warning=MODULE_TYPELESS_PACKAGE_JSON --test tests/benchmark.test.mjs` : **3 tests passent**, durée du processus 0,183 s.
- `node --check scripts/discover_samples.mjs` et `git diff --check` passent.
- Une exécution sans dérive garde la démo synthétique et `registry_updated=false`.
- Un moteur modifié, un helper modifié ou un manifeste sans l'empreinte requise sont rejetés. Le test du moteur confirme que le code sentinelle non vérifié n'est pas exécuté.

## Petit contrôle de coût

Cinq paires base/correction, ordre alterné, dans des checkouts temporaires, avec des subprocess Node neufs et un timeout de 5 secondes chacun. Médianes de temps complet : **150.95 ms avant**, **159.49 ms après**. Ce temps comprend démarrage, chargement, recherche, sérialisation et écriture du rapport. Candidats et erreurs validation/test identiques dans les cinq paires. Les temps bruts figurent dans `reports/samples-provenance-20261103.json`.

Sonde courte et bruitée sur VM, pas de benchmark statistique ni d'accélération revendiquée. Aucun coût Python/C n'est mesuré ici. Node v24.19.0, Python 3.12.14, base `ee0e9fe86a2cd89546ed3771273325b8ec7bab61`.

## Périmètre de confiance et suite

Le manifeste local est supposé fiable : ce contrôle détecte une dérive par rapport au checkout, pas une modification simultanée du moteur et du manifeste. Il ne constitue ni une signature amont ni une sandbox. Les données sont synthétiques, aucune donnée client ou relation causale n'est validée. Les rapports historiques ne sont pas réécrits.

Issue liée : #8, laissée ouverte car données réelles et validation métier restent à obtenir. La draft PR #9 sur les bornes du holdout reste indépendante et non fusionnée. Aucun changement visuel : vérification de rendu sans objet.

Triple Helix : lecture de la méthode et de l'état, priorité à un seul défaut reproductible, contre-exemples avant correction, tests et mesures par outils, rétrospective enregistrée. Adaptations automatiques toujours désactivées ; aucune métrique de convergence inventée.
