# Synthèse du chantier

## Livré et exécuté

Prototype Python sans dépendance : registre SiLU/GELU importé depuis une révision Superspear figée, empreintes vérifiées, compilation d'AST à opérateurs autorisés, routage explicite et CLI JSON. Quatre tests passent ; mesures locales disponibles dans baseline.json. Les fonctions mathématiques directes restent plus rapides ; aucune accélération SIMD ni économie LLM n'est revendiquée.

## Assemblage retenu

- Superspear possède les formules, la recherche évolutive et leur validation. Ne pas réécrire son moteur dans Frankenspear.
- SpearVM est un backend natif optionnel ; l'activer uniquement sur gain mesuré à précision et domaine comparables.
- Frankenspear fournit des idées de routage, cache et adaptateurs LLM. Éviter ses copies manuelles de formules et valider le routage sur de vraies tâches.
- Pomerado/browser-bot fournit les automatisations rejouables, les jobs et les questions utilisateur. Revoir tous les chemins d'autorisation avant connexion.
- REA fournit une couche d'investigation séparée : preuves, emplacements source, distinction observation/inférence, interface CLI/MCP commune et adaptateurs spécialisés. Lire un dépôt source ne nécessite pas de lancer Hopper/Ghidra.

## Découverte : connectée en mode borné

Superspear possède scripts/discover.ts et un outil MCP discover. La CLI prend une formule cible et un domaine, puis --rows et --gens. Elle cherche une approximation d'une cible fournie : ce n'est pas la preuve d'une nouvelle loi physique. Le prototype appelle désormais evolve depuis les deux fichiers upstream figés, sans npm install. Le wrapper utilise une graine fixe, un petit budget, un timeout de 5 secondes et un holdout de 127 points. Voir discovery.json et README.md pour l'état courant.

Mesures intégrées : pré-évaluer la cible une seule fois (la CLI inspectée réévalue le vecteur complet dans chaque itération de construction des données), imposer un petit budget, un timeout de processus, une graine reproductible et un holdout indépendant. Enregistrer les candidats à part ; aucun remplacement automatique du registre validé. Les speedups du rapport CLI sont des rapports de coûts modélisés, pas des accélérations mesurées.

## REA et skills

Dépôt inspecté : bahira/rea. Il contient skills/reverse-engineer-anything. REA couvre notamment analyse native via Hopper/Ghidra, inspection JS/source maps et observation navigateur. Aucun moteur REA installé ni exécuté ici. La skill appelée « triple X » n'a pas été identifiée dans le catalogue de skills connecté ; son usage n'est pas revendiqué.

## Prochaines étapes, petites et vérifiables

1. Découverte Superspear connectée : 9 tests passent en moins de 0,5 s. x² exact ; autres candidats insuffisants rejetés. Étendre ensuite les cas indépendants et ajuster les budgets uniquement sur besoin.
2. Comparer un seul kernel sur un backend natif optionnel, coût d'appel inclus.
3. Brancher une automatisation navigateur en lecture puis un adaptateur LLM explicite.
4. Ajouter l'interface d'investigation REA seulement pour les tâches qui en ont besoin.

Le sprite est un asset distinct : il n'intervient pas dans le runtime numérique et n'est pas activé comme avatar de la session.
