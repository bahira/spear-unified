# Parité entre score de recherche et arbre retourné — 17 novembre 2026

Le score utilisait a*pred+b avant simplification de l’arbre affine ; les rapports évaluaient l’arbre simplifié. Un arrondi de constante pouvait ainsi ne pas être compté pendant la sélection. Cas témoin y=0,123456789 : ancienne fitness -1e-7, alors que la MSE de l’arbre retourné vaut 4,4521e-14 et sa pénalité de complexité 1e-7.

Correction : après wrapAffine, évaluer l’arbre produit sur les x d’apprentissage, vérifier des prédictions finies et utiliser ces mêmes valeurs dans le score. `training_objective` expose best_fitness et complexity_cost pour rapprocher la fitness de -(MSE apprentissage + pénalité). Validation et test ne participent toujours pas à la sélection. Vendor et checksums inchangés. Cette modification peut modifier les candidats futurs quand simplification et calcul affine diffèrent ; elle ne corrige pas le conditionnement du scaling GP.

Trois tests ajoutés : constante arrondie, constante exactement représentable, démo par défaut. Avec instrumentation de sortie uniquement, l’ancienne version échoue sur la constante arrondie : différence de fitness 4,4521e-14. Après correction : 37 tests Python passent en 4,113 s, 3 tests Node en 0,205 s ; git diff --check passe. Aucune installation.

| Mesure | Avant | Après |
|---|---:|---:|
| Écart fitness attendue/observée, constante | 4,4521e-14 | 0 |
| MSE de l’arbre retourné, constante | 4,4521e-14 | 4,4521e-14 |
| RMSE validation, démo | 0,00564484 | 0,00564484 |
| Médiane processus complet, 3 paires démo | 182,10 ms | 198,12 ms |

Trois paires alternées sur démo et une paire sur constante : candidat identique dans les quatre cas. Ce contrôle corrige la notation, pas la précision du candidat observé. Une évaluation d’arbre est ajoutée par tentative de score. Échantillon temporel bruité : aucun gain revendiqué. Le JSON voisin contient les temps de recherche séparés, fitness, erreurs et instrumentation de base. Processus complet : démarrage Node, vérification des sources, recherche et rapports ; exécution isolée d’une formule et coût Python/C non mesurés.

Données synthétiques, une graine, aucune garantie continue, nouvelle loi physique, significativité ou validation client. Domaine démo généré [-2,2], plage d’apprentissage [-1.975,1.9], un point test hors plage ; constante témoin sur train x=0..7 et validation décalée de 0,25. Aucun candidat promu. Aucun changement visuel applicatif ; le tableau ci-dessus provient du JSON vérifié, aucune capture d’interface requise.

Suite : stabilité du scaling GP ou jeu réel autorisé avec partitions documentées. Issue #8 reste ouverte. Rétrospective locale session 12 : adaptation désactivée, signaux indéfinis null, pas de rétrospective décennale due (dernière session 10).
