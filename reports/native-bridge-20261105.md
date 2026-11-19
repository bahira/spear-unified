# Pont Python/C sur buffers — 5 novembre 2026

## Changement unique

Ajout d’une expérience autonome `scripts/bench_native_bridge.py` pour mesurer le kernel C depuis Python, avec une entrée et une sortie `array('d')`. Les fonctions C de référence et Taylor7 sont réutilisées depuis `scripts/native_probe.py` ; aucune formule de champion n’est recopiée et aucun nouveau moteur n’est installé. Les sources sont compilées dans un répertoire temporaire puis supprimées. Le runtime et le choix de backend restent inchangés.

## Qualité et repli

Domaine d’approximation [-1,1], tolérance expérimentale 3e-6. Hors domaine ou avec une tolérance inférieure, appel à `sin` de libm. Vérification indépendante par Python `math.sin`, bornes incluses. Tests : valeurs immédiatement au-delà des bornes, entrées finies, types, longueur, tolérances invalides, entrée inchangée, sortie vide et tolérance stricte. Le polynôme est un Taylor7 classique, pas une découverte GP ni une loi nouvelle.

## Protocole et coûts

Même entrée double contiguë déjà construite, nouvelle sortie double pour chaque variante. Validation de finitude, allocation sortie, vues ctypes, appel C, validation de tolérance et consommation de la sortie inclus. Référence Python : même scan de finitude et même type de sortie. Trois préchauffages, 11 échantillons par variante, ordre tournant et inversé. Deux processus indépendants, avec compilation locale à chaque fois.

**Exclus du temps d’appel :** construction initiale du buffer, compilation et chargement à froid (compilation rapportée séparément), démarrage CLI/JSON, conversion depuis une liste et pipeline applicatif. Le gain ne s’applique donc pas automatiquement à une API JSON ou à des listes.

| Taille | Python µs | C référence µs | C Taylor7 µs | Gain vs Python, essai 1 | Essai 2 |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.66 | 2.10 | 2.08 | 0.32× | 0.23× |
| 64 | 8.65 | 7.45 | 7.11 | 1.22× | 1.39× |
| 4096 | 474.55 | 224.11 | 204.84 | 2.32× | 1.98× |
| 65536 | 7116.50 | 3302.03 | 2835.42 | 2.51× | 2.43× |

À 65 536 éléments, gain vs C libm de 1.16× et 1.26× : une grande partie du gain contre Python vient donc du chemin natif et de l’évitement des conversions, pas uniquement de l’approximation.
Erreur maximale observée : 2.73083964e-06. À 4 096 éléments, le gain Taylor/libm change de sens entre les essais : aucun ordre robuste n’est établi à cette taille.

Premier essai : build 47.3 ms, expérience complète 0.312 s. Second : build 71.1 ms, expérience 0.422 s.

## Vérifications et limites

- `python -m unittest discover -s tests -v` : 14 tests passent en 0,792 s, dont trois tests du pont C. Les tests natifs sont ignorés explicitement si Linux ou le compilateur déjà présent est absent.
- `node --disable-warning=MODULE_TYPELESS_PACKAGE_JSON --test tests/benchmark.test.mjs` : 3 tests passent, processus 0,228 s.
- `git diff --check` : propre.
- Données brutes, flags et empreinte du code C : `reports/native-bridge-20261105.json` et `reports/native-bridge-20261105-repeat.json`.

Mesures locales courtes et bruitées, données synthétiques et Linux uniquement pour ce pont. Pas de certificat sur le domaine continu, pas de gain client démontré, pas d’activation automatique. Le petit lot d’un élément perd dans les deux essais. Aucun changement visuel ; contrôle de rendu sans objet. Aucun fichier compilé n’est publié.

## Suite

Issue #4 laissée ouverte : comparer le coût de conversion depuis les véritables entrées du pipeline avant toute sélection de backend ou intégration au runtime. Draft indépendante des PR #9 et #10, aucune fusion automatique. Triple Helix : priorité à un seul coût manquant, baseline forte libm et Python, contrôles par outils, résultats négatifs conservés et rétrospective enregistrée.
