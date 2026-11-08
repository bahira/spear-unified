# Conversions listes et JSON autour du pont C — 8 novembre 2026

## Amélioration unique

La draft PR #11 mesure les appels sur des buffers double déjà construits. Cette extension ajoute une expérience autonome `scripts/bench_native_conversion.py` qui mesure les conversions manquantes avec une référence Python, C libm et C Taylor7. Aucun changement au runtime ni à la sélection de backend ; les fonctions C et le pont existants sont réutilisés. Compilation dans un répertoire temporaire, aucune installation ni publication de binaire.

## Contrats et coûts inclus

- Liste : validation numérique, construction `array(d)`, second contrôle de finitude du pont, allocation de sortie, vues ctypes et appel C, conversion du résultat vers une liste. La référence Python valide la liste et retourne également une liste via `math.sin`.
- JSON : mêmes opérations plus décodage de l’entrée et encodage de la liste de sortie pour les trois variantes. Le payload d’entrée est déjà encodé avant le chronométrage, comme une requête reçue ; l’encodage initial de l’entrée n’est pas compté.
- Préchauffage : 2 passages ; 7 échantillons, ordre tournant et inversé ; temps bruts conservés. Deux processus indépendants, reconstruction de la bibliothèque à chaque fois.

Restent exclus : génération des entrées synthétiques, compilation/chargement à froid, démarrage CLI/processus, réseau et pipeline client. Les buffers sont recréés à chaque appel des variantes natives. Les sorties approximatives peuvent avoir des chiffres et des longueurs JSON différents ; ces tailles sont consignées, et leur coût de sérialisation fait partie de la mesure.

## Résultats

| Format | Taille | Python ms | C libm ms | C Taylor7 ms | Ratio vs Python, essai 1 | Essai 2 |
|---|---:|---:|---:|---:|---:|---:|
| list | 1 | 0.0005 | 0.0027 | 0.0027 | 0.203× | 0.194× |
| list | 64 | 0.0062 | 0.0111 | 0.0104 | 0.597× | 0.600× |
| list | 4096 | 0.3882 | 0.5691 | 0.5191 | 0.748× | 0.770× |
| list | 65536 | 6.5333 | 9.4589 | 8.9857 | 0.727× | 0.733× |
| json | 1 | 0.0033 | 0.0054 | 0.0053 | 0.631× | 0.595× |
| json | 64 | 0.0406 | 0.0457 | 0.0454 | 0.895× | 0.883× |
| json | 4096 | 2.8004 | 3.0492 | 2.7826 | 1.006× | 0.882× |
| json | 65536 | 43.2097 | 45.8449 | 44.5838 | 0.969× | 0.957× |

Un ratio inférieur à 1 signifie que le natif approché est plus lent. Les listes perdent à toutes les tailles dans les deux processus. Le JSON 4096 franchit légèrement 1 au premier essai, puis retombe sous 1 : pas de gain robuste. À 65536, JSON est plus lent dans les deux essais. Le gain des buffers préexistants ne se transfère donc pas à ces chemins de conversion.

## Précision et contrôles

Domaine synthétique [-1,1], erreur absolue maximale observée 2,73084e-6, budget 3e-6. Hors domaine ou budget plus strict, le pont utilise libm. Taylor7 est une approximation classique, pas une formule découverte par GP. Les tests contrôlent précision, repli, types de sorties, non-mutation, tolérance stricte, sortie vide et rejet d’entrées invalides avant le C.

- `python -m unittest discover -s tests -v` : **17 tests passent en 0,559 s**.
- `node --disable-warning=MODULE_TYPELESS_PACKAGE_JSON --test tests/benchmark.test.mjs` : **3 tests passent**, processus 0,187 s.
- `git diff --check` : propre.
- Premier build 41.99 ms, expérience complète 1.847 s ; second build 39.49 ms, expérience 1.844 s.

Preuves : `reports/native-conversion-20261108.json` et `reports/native-conversion-20261108-repeat.json`, avec versions, flags et empreinte du code C. Le test natif exige Linux et un compilateur déjà présent ; il est ignoré explicitement s’ils manquent.

## Limites et décision

Sonde courte et bruitée sur VM, sans données client ni certificat sur l’intervalle continu. Aucune accélération applicative ou économie commerciale annoncée. On ne choisit pas automatiquement C pour des listes/JSON ; le runtime reste inchangé. Mesurer un pipeline réel ou identifier des entrées déjà contiguës avant une intégration. L’issue #4 reste ouverte et la PR reste draft, sans fusion automatique.

Aucune modification visuelle : contrôle du rendu sans objet. Triple Helix appliqué : une seule lacune de mesure priorisée, baseline forte, contrôle indépendant Python math, deux essais, résultats négatifs conservés et état mis à jour en fin d’itération.
