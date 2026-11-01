# Pousser Discovery : usages voisins et choix de méthode

## Point clé

Le produit utile est un petit laboratoire de modèles compacts : proposer une relation, comparer des alternatives simples, vérifier la qualité et mesurer son intérêt applicatif. La recherche évolutive n'est qu'une méthode parmi d'autres ; elle n'a pas à gagner systématiquement. Le meilleur résultat peut être une simplification classique, une interpolation ou l'absence de changement.

## Pistes voisines

| Piste | Exemple concret | Méthode de référence à battre | État / difficulté |
|---|---|---|---|
| Calibration interprétable | Convertir la lecture d'un capteur en mesure corrigée | Affine, polynôme bas degré, table de calibration | Première démo sur données synthétiques ; vrai jeu capteur encore absent |
| Modèle de coût système | Estimer la latence d'un lot selon sa taille | Mesure directe, modèle affine/par morceaux | Nécessite collecte réelle, plusieurs charges, validation hors exécution et dérive |
| Surrogate de simulation | Remplacer un solveur coûteux sur une zone de paramètres | Interpolation, polynôme, approximation rationnelle | Pertinent si le domaine est borné ; coût de collecte et erreur de sortie à mesurer |
| Approximation de fonctions | sin, exp, activations sur intervalle borné | Bibliothèque optimisée, Taylor/Chebyshev/minimax, table | Premières sondes disponibles ; meilleure baseline indispensable |
| Simplification exacte | exp(log(x)) → x sous conditions | Simplification algébrique, réécriture d'expressions | Éviter une recherche coûteuse si une identité prouvée suffit ; rails numériques et domaine comptent |
| Auto-tuning de backend | Choisir scalaire/vectoriel, taille de lot, fusion | Runtime existant, BLAS/libm optimisés | Compiler une variante puis profiler ; aucun gain à extrapoler de l'AST |
| Cache / réutilisation | Réponses identiques ou intégrations navigateur rejouées | Cache simple avec invalidation | Mécanisme distinct, souvent plus rentable que réinventer une formule |
| Compression / distillation | Petit modèle reproduisant un modèle coûteux | Petit réseau ou régression supervisée | Mesurer qualité finale, dérive, coût de collecte et décision de repli |
| Identification dynamique | Retrouver une équation différentielle d'un système | Modèle physique, régression parcimonieuse de dérivées (type SINDy) | Pas disponible actuellement ; unités, dérivées bruitées et expérience contrôlée nécessaires |
| Règles interprétables de décision | Routage de tâches selon des caractéristiques | Règles simples, régression logistique | Données étiquetées et coût des erreurs requis ; pas du raisonnement général |

## Priorité sur machine modeste

1. **Calibration scalaire sur points** : peu d'observations, expressions courtes, baseline affine et quadratique, train/validation/test distincts. Identifier rapidement si la recherche apporte autre chose qu'un ajustement polynomial.
2. **Modèle de coût sur mesures CPU locales** : collecte bornée, puis modèle simple pour décider d'une taille de lot. Vérifier sur d'autres exécutions ; ne pas apprendre le bruit d'une VM comme une loi générale.
3. **Une approximation appliquée à un pipeline complet** : utiliser les sondes sin comme candidats, mesurer la fraction du temps réellement accélérable et le coût du passage de langage.

## Ce qu'une démo ne prouve pas

Un fit sur des points synthétiques confirme un chemin technique. Il ne valide ni un secteur, ni une relation causale, ni un prix commercial. Une meilleure erreur d'apprentissage ne suffit pas. Une formule moins chère en unités d'opérations peut être plus lente sur un CPU réel. Réutiliser les mêmes points pour choisir puis certifier la formule crée un biais de sélection.

## Protocole de décision

- Définir l'entrée, la sortie, le domaine, les unités, le coût initial et la tolérance liée à l'usage.
- Comparer d'abord une baseline forte et simple ; séparer train/validation/test selon le temps, les groupes ou l'hypothèse i.i.d.
- Ajuster uniquement sur train ; sélectionner sur validation ; réserver test à la conclusion finale. Après modification guidée par test, prévoir un autre test indépendant.
- Rapporter erreur absolue et métrique métier ; ajouter erreurs relatives seulement là où le dénominateur a un sens.
- Mesurer temps complet, allocations, conversions et comportement hors domaine ; revenir à la référence si nécessaire.
- Ne promouvoir que si qualité et intérêt applicatif sont établis. Garder aussi les résultats négatifs.

Sources de vérité : code de l'adaptateur dans spear/discover.mjs, moteur importé vendor/superspear/engine.ts, rapports domain-probes.json, discovery-domains.md, native-probe.md et validation-update.md. Les méthodes citées sont des alternatives techniques établies, pas des fonctions déjà implémentées dans ce projet.
