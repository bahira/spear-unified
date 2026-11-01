# Pareto-Caveman : utile dans les instructions permanentes ?

## Recommandation

Oui pour un noyau court de priorisation ; non pour l'application littérale et systématique d'un quota de 20 % à chaque demande. Le texte complet de Triple Helix reste une procédure à charger pour les tâches complexes. Aucun bénéfice chiffré sur le modèle n'a été mesuré ici.

## Ce que dit effectivement la skill

Source fournie : `.agents/skills/triple-helix/SKILL.md`, section « Loop 1 — Tactical (Pareto-Caveman) ».

- But déclaré : « cut 80% of noise, keep top 20% by impact ».
- Étape 3 : « Keep top pareto_ratio (default 0.20 ...) ». Le reste est marqué skipped.
- Exceptions : « spec_critical=True » et les types verrouillés tels que math_proof/security_review.
- La boucle stratégique peut rétablir un élément ignoré dont dépend le résultat.

Le principe 80/20 est une heuristique, pas une preuve que 80 % d'une demande donnée est inutile. Les durées « ~ms » et les bénéfices déclarés dans le document ne sont pas des mesures instrumentées de ce projet.

## Effets plausibles à vérifier

- Moins de travail accessoire, moins d'installations et de recherches sans effet sur le livrable.
- Première preuve utile plus tôt : un petit test, une baseline, une mesure réelle.
- Réponses plus courtes et moins de compte rendu procédural, si la procédure reste principalement interne.
- Meilleure maîtrise des ressources : ne pas lancer un build global lorsqu'un test ciblé suffit.

Ces effets dépendent de la qualité de la priorisation. Une tâche notée faible impact peut être une dépendance critique. Les scores de l'agent ne sont pas des probabilités calibrées ni des mesures objectives.

## Risques d'une intégration intégrale à chaque tour

| Risque | Exemple | Garde-fou |
|---|---|---|
| Sous-livraison | Ignorer une partie explicite du besoin au nom des 20 % | Toutes les exigences utilisateur restent obligatoires |
| Mauvaise dépendance | Benchmarker sans vérifier le domaine | Restaurer les prérequis et tester les hypothèses |
| Coût de procédure | Journaliser quatre boucles pour une question simple | Exclure les réponses simples ; procédure complète conditionnelle |
| Inventions de métriques | Annoncer 95 % de convergence sans dénominateur défini | Conserver preuves brutes ; métrique inconnue = null |
| Contexte encombré | Charger tout le document à chaque réponse | Court noyau permanent et référence au fichier complet |
| Règles contradictoires | CSR interprété dans deux sens dans la skill | Adaptations automatiques désactivées, convention à clarifier |

## Texte court proposé pour des instructions de projet

> Pour les tâches complexes, priorise les actions qui produisent vite une preuve utile et un livrable vérifiable. Conserve toutes les exigences explicites, les dépendances et les contrôles nécessaires. Réduis le travail facultatif sans quota fixe. Commence par une itération courte ; rétablis une action différée dès que les résultats montrent qu'elle est nécessaire. Distingue ce qui est mesuré, supposé et non réalisé. Charge la procédure Triple Helix complète lorsque la complexité le justifie.

C'est une proposition de consigne, pas une modification du prompt système de la plateforme. Le projet dispose déjà d'AGENTS.md et de la skill locale pour une persistance dans ce dépôt. La relecture de ces fichiers aide aux sessions futures qui ont accès au dépôt ; elle ne garantit pas que tous les clients ou modèles les chargent automatiquement.

## Comment tester si cela améliore le travail

Comparer un petit ensemble de tâches comparables avec et sans ce noyau, en gardant modèle, outils et budgets identiques autant que possible. Mesurer : exigences satisfaites, défauts trouvés par un contrôle indépendant, durée totale, appels/outils et retouches nécessaires. Inclure une tâche simple, une correction, une analyse et une tâche à dépendances. Répéter pour limiter l'effet du bruit ; ne pas conclure à partir d'une réponse plus courte seulement.

Pas d'adaptation automatique des seuils tant qu'il n'existe pas de mesures fiables et de règles cohérentes. Dans notre chantier, les effets sont illustrés par le choix de petits benchmarks et de baselines fortes ; ce n'est pas une expérience A/B du prompt.
