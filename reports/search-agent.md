# Recherche courte de candidats

Six cibles testées en ~0,76 seconde au total, sans installation : 64 points d'apprentissage, population 64, 30 générations, graine 42. Résultats bruts et benchmarks : `search-agent.json`.

## Candidat à examiner

- Cible : `exp(log(x))`, domaine **[0.1, 2]**.
- Candidat réellement trouvé : `sq(x) + (x - sq(x))`.
- Erreur max sur holdout upstream : 5,55e-17. Contrôle Python indépendant de 10 001 points, bornes incluses : erreur d'arrondi négligeable (voir JSON).
- Benchmark même évaluateur vectoriel upstream, allocations comprises : **61,17 → 16,44 ns/élément**, rapport médian **3,72×**. 4 096 points, 50 préchauffages, 31 répétitions de 16 passages, ordre alterné.
- Ce candidat redécouvre une identité connue et contient lui-même une redondance : la simplification finale naturelle est `x`. Il démontre la chaîne recherche/validation/mesure, pas une nouvelle loi. Comparer aussi à `x` directement avant toute promotion ; le gain ne justifie pas de stocker cette expression encombrée.
- Domaine limité : ne pas généraliser aux entrées négatives ou extrêmes, car les règles protégées log/exp upstream changent la cible.

## Autres résultats

- `sqrt(x*x)` sur [0,2] : même candidat, précis mais ~0,996×, donc aucun gain mesuré.
- `sin(x)^2 + cos(x)^2`, polynôme `(x+1)^2`, `sin(x)` sur [-0.1,0.1], `exp(x)` sur [-0.1,0.1] : candidats rejetés au seuil 1e-4.

Aucun fichier de code partagé modifié et aucun candidat ajouté au registre. Timings locaux courts, sensibles à la VM ; pas de revendication C/SIMD/end-to-end.
