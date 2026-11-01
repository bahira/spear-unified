# Audit court du benchmark et de la découverte

Audit statique des quatre fichiers demandés, sans nouvelle exécution ni changement au code partagé.

## Verdict sur les chiffres existants

La conclusion « aucun gain utile validé » est correcte. Le seul candidat précis est x² : le gain apparent de 1,08× est petit face aux variations observées (base 3,13–12,43 ns/élément, candidat 3,38–7,78). Les deux autres gains ne sont pas recevables car leur erreur dépasse la tolérance. Le contrôle direct est correctement présenté comme deux implémentations identiques, pas comme un backend compilé de la découverte.

Le protocole est raisonnable pour une sonde rapide : même évaluateur, mêmes données et allocations de sortie, préchauffage, ordre alterné, médianes. Il mesure l'interpréteur vectoriel, pas un gain intrinsèque des formules ni C/WASM/SIMD. Dans l'évaluateur, mul(x,x) et sq(x) font la même multiplication ; sq économise seulement un passage de dispatch/récursion.

## Défaut principal à corriger avant d'étendre les cas

Le benchmark construit une seule grille [-2,2] et ignore r.config.lo/hi. Les records actuels utilisent tous ce domaine, donc leurs mesures restent cohérentes. Toute prochaine recherche sur un autre domaine sera benchmarkée et déclarée eligible sur le mauvais domaine. Construire xs par record à partir de config.lo/hi et enregistrer ce domaine dans chaque résultat.

## Autres limites et améliorations ciblées

1. Ajouter un contrôle Number.isFinite sur les références, candidats, erreurs et statistiques. Un débordement de MSE est possible pour de grandes amplitudes : le runner vérifie l'erreur individuelle mais pas sa somme de carrés. JSON.stringify convertirait Infinity en null ; rejeter explicitement les métriques non finies avant sérialisation.
2. duration_ms commence après parsing et préparation des cibles : c'est le temps recherche + holdout, pas le coût complet de la commande. Ajouter elapsed_total_ms côté Python autour du subprocess ; ne pas comparer la durée de recherche aux ns/élément.
3. Les 127 points de holdout ne sont jamais utilisés par la fitness : bon. Ils restent une grille déterministe intérieure, sans bornes, et partagent l'évaluateur et les rails de la cible ; ce n'est pas une référence mathématique indépendante ni une garantie continue. Ajouter les deux bornes, quelques points indépendants et un oracle Python/C ciblé pour toute promotion.
4. Sauver les temps appariés (ou médiane des rapports par paire) pour juger les petits gains ; ne pas imposer une certification statistique lourde. Une répétition dans un second processus peut confirmer un gain important.
5. Le heap V8 de 128 Mio n'est pas une limite RSS totale ; le timeout de 5 s tue le processus Node, ce qui est suffisant pour ce wrapper sans enfants. La graine 0 est ramenée à 1 par le moteur : documenter effective_seed si nécessaire.
6. La provenance source_commit vient de source.json, sans vérification des fichiers vendor à chaque appel. Les empreintes sont disponibles ; les vérifier une fois avant de revendiquer la révision exécutée.

Priorité : domaine par candidat, métriques finies, temps complet ; ensuite référence indépendante pour le premier vrai gain.
