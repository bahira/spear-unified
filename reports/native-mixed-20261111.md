# Mélange de domaines et repli libm — 11 novembre 2026

## Amélioration unique

Expérience autonome `scripts/bench_native_mixed.py` : comparer Python, C exact et C avec repli sur des buffers déjà construits, pour 0 %, 50 % et 100 % de points hors domaine. Le pont et le code C de la PR #11 sont réutilisés sans modification. Rien n’est ajouté au runtime ni sélectionné automatiquement.

Les cas sont synthétiques et déterministes, intercalés de façon régulière. Domaine d’approximation [-1,1], points extérieurs de valeur absolue entre 2 et 8, budget 3e-6. Deux tailles (4096 et 65536), deux processus indépendants, sept échantillons par variante, deux préchauffages, ordre tournant et inversé.

## Précision et comptes

Le nombre d’approximations doit égaler la taille moins le nombre réel de points hors domaine. Ces points extérieurs sont contrôlés indépendamment contre Python math.sin (tolérance de vérification 1e-14). Les tests contrôlent aussi les comptes, l’absence de mutation et l’erreur maximale globale.

Avec 100 % de points extérieurs : zéro approximation et erreur maximale mesurée nulle. Sur les cas contenant des points intérieurs, erreur maximale observée 2,73084e-6, sous le budget. Ces observations sur des grilles ne certifient pas le continu. Taylor7 est classique, pas une formule découverte par GP.

## Mesures et coûts

| Taille | Hors domaine | Approximations | Python ms | C exact ms | C mixte ms | Ratio vs C exact, essai 1 | Essai 2 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4096 | 0 % | 4096 | 0.3922 | 0.1872 | 0.1631 | 1.147× | 1.196× |
| 4096 | 50 % | 2048 | 0.3912 | 0.1905 | 0.1724 | 1.105× | 1.010× |
| 4096 | 100 % | 0 | 0.4407 | 0.2608 | 0.1927 | 1.354× | 1.030× |
| 65536 | 0 % | 65536 | 7.0026 | 3.1618 | 2.8261 | 1.119× | 1.205× |
| 65536 | 50 % | 32768 | 6.5316 | 3.1418 | 2.7880 | 1.127× | 1.210× |
| 65536 | 100 % | 0 | 6.7781 | 3.4043 | 3.4001 | 1.001× | 1.044× |

Les ratios de temps ne suffisent pas à attribuer un gain à une approximation : à 100 % hors domaine, aucune approximation ne tourne. Le rapport 1,354× du premier essai à 4096 éléments retombe à 1,030× au second. Le parcours et le bruit peuvent faire varier la mesure ; aucun avantage de l’approximation n’est revendiqué pour ce cas. Comparer à Python seul masquerait cette distinction, car le parcours C peut être plus rapide sans approximation.

Inclus : scan de finitude, allocation de sortie, vues ctypes, appel C, validation de tolérance et lecture de sortie. Python prend le même buffer d’entrée et produit le même type de sortie. Exclus : construction initiale du buffer, compilation/chargement à froid, démarrage CLI, conversions listes/JSON, réseau et application réelle. Les conclusions négatives des listes/JSON du 8 novembre restent valables pour ces mesures distinctes.

## Vérification et budget

- `python -m unittest discover -s tests -v` : **18 tests passent en 0,741 s**, avec le nouveau test des mélanges et les contrôles précédents.
- `node --disable-warning=MODULE_TYPELESS_PACKAGE_JSON --test tests/benchmark.test.mjs` : **3 tests passent**, processus 0,302 s.
- `git diff --check` : propre.
- Essai 1 : compilation 42.7 ms, total 0.643 s. Essai 2 : compilation 72.2 ms, total 0.665 s.

Données brutes : `reports/native-mixed-20261111.json` et `reports/native-mixed-20261111-repeat.json`. Empreinte du C et flags enregistrés ; bibliothèque compilée dans un répertoire temporaire et non publiée. Aucun paquet installé.

## Limites et suite

Un mélange déterministe ne représente pas une distribution client ; ordre des valeurs, cache, prédiction de branche et bruit de VM peuvent changer les résultats. Aucun gain applicatif, économie commerciale ou politique de sélection générale établi. L’issue #4 reste ouverte : il faut qualifier le format mémoire et la proportion réelle de repli dans un pipeline représentatif. La PR #11 reste draft sans fusion.

Triple Helix : une lacune de mesure priorisée, référence forte C exact, oracle indépendant et compte d’approximations, deux essais et résultats négatifs conservés ; aucune adaptation de seuil. Pas de modification visuelle : vérification du rendu sans objet.
