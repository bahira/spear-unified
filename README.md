# SPEAR Unified — prototype léger

Socle local sans dépendance externe ni service : Python 3.10+ suffit.

```sh
python -m spear '{"kind":"compute","kernel":"silu","x":1}'
python -m unittest discover -s tests -v
python bench.py
```

## Ce qui fonctionne

- Registre unique de deux enregistrements Superspear (SiLU, GELU), importés à une révision figée et contrôlés par SHA-256 au chargement.
- Compilation des arbres JSON vers un AST Python à opérateurs autorisés ; aucun texte de formule n'est exécuté. Les divisions protégées, clamps et approximation erf suivent la source.
- Routage explicite des tâches structurées ; réponse JSON avec provenance.
- Mesure locale bornée : 1 001 valeurs, 5 passages, comparaison à math.exp/math.erf et mesure des variantes fast, désactivées en production.
- Tests numériques indépendants, entrées non finies, règles numériques, opérateurs inconnus et absence de repli externe silencieux.

## État réel

Les adaptateurs navigateur et LLM renvoient `unavailable` : ils ne sont pas encore connectés. SpearVM n'est pas installé et aucun gain natif n'est revendiqué. Pas de classifieur de langage naturel, de serveur, d'entraînement ou d'appel payant. Aucun dépôt distant modifié.

Les champions sont plus lents que les références mathématiques directes dans ce premier moteur Python. Le but de cette étape est une sémantique traçable et mesurable, pas une promesse d'accélération. Les timings de quelques microsecondes sont bruités et propres à cette VM.

La grille [-8,8] sert de sonde locale ; elle ne certifie pas le domaine de déploiement. Une variante fast ne sera retenue qu'avec un budget d'erreur explicite et un gain end-to-end. Les records upstream restent intacts ; aucune copie manuelle de leur formule dans le runtime.

## Architecture cible et étapes courtes

1. Superspear : source unique des formules et audits (premier import réalisé).
2. Sélecteur de backend : comparer Python de référence, C/WASM et SpearVM, en conservant précision et règles numériques ; choisir seulement sur preuves locales.
3. Frankenspear : reprendre l'idée de routage et les adaptateurs, sans ses copies de formules et sans réutiliser les économies LLM estimées comme mesures réelles.
4. Browser-bot/Pomerado : brancher séparément les tâches asynchrones. Vérifier l'autorisation de chaque chemin d'écriture, y compris le rejeu `browser_run`, avant activation.

Politique d'itération : tests ciblés puis mesure courte, pas de build global ni de gros entraînement. Aucune dépendance lourde sans besoin mesuré.

Sources : https://github.com/bahira/superspear ; https://github.com/bahira/SpearVM ; https://github.com/bahira/frankenspear ; PR https://github.com/bahira/superspear/pull/10.
Les données importées sont sous MIT ; attribution dans LICENSE.upstream et provenance dans spear/data/source.json.

## Découverte connectée

Node 22.18+ ou 24+ exécute directement les deux fichiers TypeScript importés ; aucun npm install ni build global.

```sh
python -m spear '{"kind":"discover","formula":"x*x","seed":42}'
```

Budget par défaut : 64 points, population 32, 8 générations ; limites : 256 points, population 64, 30 générations ; arrêt du processus à 5 secondes et limite de heap V8 à 128 Mio (pas une limite de mémoire totale). La cible est évaluée une seule fois par jeu de données. Une graine fixe reproduit le candidat.

Validation sur 127 points distincts de l'apprentissage. `accepted_on_probe` compare l'erreur maximale à `max_abs_error` (défaut 1e-4) ; ceci ne certifie ni le domaine continu ni une nouvelle loi physique. `status=ok` signifie que la recherche a terminé, pas que la formule est assez précise. `registry_updated=false` : aucun candidat n'est promu automatiquement. Résultats : reports/discovery.json.

Moteur et sémantique de validation upstream ; contrôle indépendant Python ajouté pour le cas x². Recherche limitée aux opérateurs algébriques add/sub/mul/sq/neg ; elle peut échouer sur des cibles simples avec ce petit budget. Les adaptateurs LLM, navigateur et SIMD restent non connectés.
