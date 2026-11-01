# Étendre la découverte à d'autres domaines

Analyse du code local : `spear/discover.mjs`, `spear/discovery.py`, moteur Superspear importé (`vendor/superspear/engine.ts`). Aucune installation ni exécution supplémentaire dans cette analyse.

## Périmètre réellement disponible

Aujourd'hui, l'entrée est **une formule cible analytique**, une seule variable nommée `x`, un intervalle et une graine. Les cibles sont évaluées avec les règles numériques protégées du moteur upstream. Les candidats sont des polynômes construits avec `add/sub/mul/sq/neg`, profondeur maximale 4, constantes initiales dans [-3,3]. Ce sont des approximations/simplifications de fonctions connues, pas une ingestion de mesures et pas une détection autonome de causalité.

Le moteur upstream accepte une liste de variables et évalue des scopes multivariables ; **le wrapper intégré refuse les autres variables**. Il manque donc une interface et une validation multivariables, pas nécessairement un nouveau moteur génétique.

Budget actuel : 8–256 points, population 8–64, 1–30 générations ; heap V8 128 Mio et timeout processus 5 s. Limite de heap ≠ mémoire totale. La recherche peut échouer très vite et proprement ; la réussite sur `x²` ne garantit rien pour une autre cible.

## Matrice d'usage

| Domaine | Possible maintenant | Manque avant usage réel | Mesure pertinente |
|---|---|---|---|
| Simulation/physique numérique | Approximer une loi scalaire connue sur un intervalle : fonction de réponse, amortissement, correction locale. | État multivariable, unités, contraintes de stabilité/positivité, tests aux régimes extrêmes ; intégrer le candidat dans le vrai solveur. | Erreur sur trajectoire/observable, stabilité, temps du solveur complet ; pas seulement ns/fonction. |
| Signal/audio/image | Approximer `sin`, courbes de transfert ou enveloppes sur un petit domaine ; comparer à des polynômes connus. | Domaines périodiques, réduction d'argument, discontinuités, biais spectral et propagation d'erreur. | Erreur max, distorsion/erreur spectrale selon usage, temps par bloc et coût des contrôles de domaine. |
| ML | Approximer une activation scalaire ou une calibration déjà formulée. | Exécution tensorielle/vectorielle, gradients cohérents, distribution d'activations réelle, tests modèle complet ; entraînement non intégré. | Qualité modèle, gradients et stabilité, latence/batch ; le coût ALU ne prédit pas le gain. |
| Finance | Explorer des approximations de courbes analytiques scalaire à paramètres fixés. | Plusieurs paramètres, contraintes de non-arbitrage/monotonie, queues/discontinuités, validation temporelle ; politique de données. | Erreur de prix et sensibilités, risques extrêmes, latence end-to-end. Aucun profit ou pouvoir prédictif établi. |
| Systèmes/performance | Simplifier une formule connue de coût, délai ou contrôleur à un paramètre. | Mesures système entrantes, bruit/hétéroscédasticité, charge changeante, objectifs et contraintes de contrôle. | Erreur en conditions non vues, stabilité du système, CPU/mémoire/latence réels, coût de sélection et d'appel inclus. |
| Données empiriques | **Non disponible** : pas d'entrée CSV/JSON de couples observés, pas de séparation expérimentale. On peut seulement fournir une formule qui imite ces données. | Adaptateur de données, contrôles de qualité, unités, splits par groupe/temps/intervention, pondération/incertitude, références simples et provenance. | Généralisation sur observations réellement réservées ; résidus, incertitude, robustesse et éventuel test interventionnel. |

## Validation : ce que le résultat prouve et ne prouve pas

- Les 127 points de holdout ont une grille décalée de la grille d'apprentissage. Ils évaluent l'interpolation **dans le même intervalle**, avec la même cible et les mêmes règles numériques upstream. Ce n'est ni une référence indépendante générale ni un test d'extrapolation. Des points distincts ne suffisent pas à rendre des données statistiquement indépendantes.
- Réutiliser cette grille pour choisir domaines, graines, opérateurs ou candidats transforme progressivement le holdout en jeu de sélection. Réserver un troisième probe final, figé à l'avance et non utilisé pour choisir, puis inclure les bornes et points difficiles. Pour des observations : split par temps/groupe/source avant la recherche.
- Les bornes exactes ne sont pas incluses dans les grilles de recherche/holdout actuelles. Les vérifier séparément et vérifier les singularités ou changements de régime. Une grille finie ne certifie pas l'erreur continue.
- L'erreur absolue seule pénalise mal des échelles mélangées : définir selon le métier une combinaison erreur absolue/relative, un plancher et des contraintes. Ne pas ajouter un critère après avoir vu le résultat pour le faire passer.
- `accepted_on_probe` signifie uniquement erreur sous le seuil demandé sur ce probe. Il ne vaut pas validation scientifique, sûreté de déploiement ou promotion du registre. `registry_updated=false` est cohérent.
- La même sémantique upstream peut masquer une erreur partagée entre cible et candidat. Ajouter une référence indépendante pour les lois connues et les cas limites ; pour les données, conserver l'observation originale avec son incertitude.

## Causalité et nouveauté

Une relation compacte ajustée à des mesures est une **hypothèse prédictive**, pas une cause. Confusions, variables omises et changement de régime restent possibles. Un résultat causal nécessite un plan expérimental/interventionnel ou des hypothèses d'identification explicites et vérifiées par le domaine ; le moteur ne les apporte pas.

La recherche sur une formule analytique fournie retrouve souvent une identité ou une approximation connue. Exemple déjà mesuré : `exp(log(x))` sur [0.1,2] peut se remplacer par `x` ; aucun caractère nouveau. Comparer à simplification symbolique, Taylor/Chebyshev/Pade selon le cas, interpolation et références usuelles avant de parler de découverte. Ni le nombre de kernels ni une erreur faible ne prouve la nouveauté.

## Multivariable et coût

Étendre d'abord à **deux variables** avec opérateurs limités, domaine rectangulaire explicite, unités et points de validation différents. Éviter une grille exhaustive : le nombre de points croît exponentiellement avec la dimension. La recherche doit rester bornée ; un petit échantillon stratifié peut servir de probe sans devenir une certification.

La fitness évalue chaque candidat sur chaque point ; le coût dépend au moins de population × générations × points × complexité d'arbre. Le tri Pareto ajoute aussi un coût dépendant de population. Les limites actuelles empêchent une montée brute en charge mais ne garantissent pas une même durée sur toutes les cibles. Mesurer `elapsed_total_ms` pour coût utilisateur ; `duration_ms` du moteur ne comprend pas tout le lancement Node et la préparation. Les ratios `cost_units` sont modélisés ; ils ne remplacent ni un microbenchmark équitable ni un gain bout en bout. Comparer aussi le coût d'appel Python/Node et l'amortissement sur le nombre d'utilisations.

## Trois POC légers, par priorité

### 1. Signal : petit angle sin(x), sans nouveau composant

- Domaine figé [-0.1,0.1], erreur max requise 1e-4 ; recherche existante, 64 points, 8 puis au plus 30 générations seulement si le premier résultat échoue.
- Références : Math.sin, `x`, Taylor degrés 3/5 (benchmarks locaux déjà disponibles). Réserver un probe final supplémentaire avant de sélectionner.
- Succès : candidat sous le seuil sur probe final + bornes et gain mesuré supérieur au bruit par rapport **au meilleur baseline éligible**, coût de contrôle du domaine inclus. Échec utile si Taylor reste meilleur ; ne rien promouvoir.

### 2. Simulation : courbe d'amortissement scalaire

- Cible connue `exp(-x)` sur [0,0.25] : un seul paramètre, domaine court, même petit budget. Comparer à fonction directe et polynômes Taylor connus ; aucune simulation complète à installer.
- Contraintes : sortie positive et décroissante sur le probe final ; erreur absolue max 1e-4 définie à l'avance. Vérifier aussi 10 001 applications répétées à un état scalaire pour mesurer l'accumulation d'erreur et le temps total, sans présenter ce jouet comme validation d'un solveur physique.
- Succès : erreur locale et erreur accumulée sous budgets explicités avant run, gain robuste face au meilleur baseline valide. Sinon conserver la référence.

### 3. Données : récupération d'une courbe de capteur synthétique avec bruit

- Petit adaptateur futur d'entrée `(x,y)` ; 96 observations synthétiques reproductibles réparties en apprentissage/validation/test final avant recherche. Loi de génération tenue hors du code de fitness ; quelques outliers et un bruit documenté pour vérifier les rejets. Aucune dépendance nécessaire pour générer le jeu.
- Comparer à constante, droite et polynôme degré 2 ; commencer à une variable. Fixer un budget recherche de 1 s et ne pas utiliser le test final pour choisir les paramètres.
- Succès : modèle compact avec erreur test comparable au niveau de bruit et au moins aussi bon que le meilleur baseline simple, sans préférence injustifiée pour une expression complexe. Vérifier qu'un jeu sans relation produit un rejet. Ce POC valide le pipeline empirique, pas une loi nouvelle ni une causalité.

## À ne pas faire pour ces POC

Pas de recherche massive de graines, pas d'entraînement ML lourd, pas de données financières réelles ni d'outils de décompilation à installer. Les résultats négatifs font partie du rapport ; pas d'intégration automatique au registre, pas d'extrapolation au-delà des domaines testés. Les usages physiques, financiers et ML restent des pistes jusqu'à preuve sur leur workflow réel.

## Mise à jour : probes exécutés pendant cette analyse

Le parent a exécuté `scripts/probe_domains.py` et enregistré `reports/domain-probes.json` :

- Signal, `sin(x)` sur [-0.1,0.1] : seuil illustratif 2e-4, erreur max ~1.6658e-4.
- Thermique, `exp(-x)` sur [0,0.1] : seuil illustratif 0.01, erreur max ~0.00906.
- ML, `tanh(x)` sur [-0.1,0.1] : seuil illustratif 0.001, erreur max ~0.000332.

Trois oracles `math` indépendants, 1 001 points chacun, bornes incluses ; ~0,42 s au total selon le relevé parent. Ces seuils servent à une démonstration de domaines et ne sont pas des critères métier établis. Ces probes ne mesurent pas la vitesse, ne prouvent pas de gain sur une simulation ou un modèle ML et ne valident pas la nouveauté. En particulier le signal accepté à 2e-4 échoue au seuil plus strict 1e-4 proposé dans le POC 1 ; conserver explicitement cette différence au lieu de fusionner les verdicts.
