# Scaling GP centré et normalisé — 18 novembre 2026

Une amélioration : l’adaptateur local de régression sur observations centre et normalise les prédictions d’apprentissage avant d’estimer leur covariance avec y. La formule précédente soustrayait des grandes sommes et appliquait un seuil absolu de variance, ce qui pouvait masquer une variation utile sur une plage étroite/décalée. Cas constant : pente nulle et moyenne de y. Les coefficients sont ensuite convertis en a,b pour wrapAffine ; la notation reste celle de l’arbre simplifié réellement retourné.

Aucun fichier vendored ni checksum modifié. Le moteur Superspear épinglé n’est pas corrigé globalement ; seul scripts/discover_samples.mjs utilise cette méthode locale, identifiée dans training_objective.scaling. Paramètres de recherche, graine, pénalité de complexité, sélection uniquement sur apprentissage et comparaisons aux baselines inchangés. Les candidats et coefficients peuvent changer, y compris à l’arrondi près dans la démo.

Tests : trois nouveaux cas (plage décalée, très petite plage à forte pente, cible constante). L’ancien adaptateur échoue sur le cas décalé de pente 5. Après correction : 40 tests Python passent en 4,215 s, 3 tests Node en 0,180 s, git diff --check passe. Les tests existants contrôlent aussi absence de fuite de validation et parité fitness/arbre.

| Données synthétiques | Erreur max validation avant | Après |
|---|---:|---:|
| x=9999+1e-4*t, y=1+5e-4*t | 5,03415e-4 | 1,35625e-11 |
| Même plage, pente 2 plutôt que 5 | 7,5e-4 | 7,5e-4 |
| x=1e-9*t, y=1+0,2*t | 1,11022e-15 | 2,22045e-16 |

Pour ces témoins, t=0..7 en apprentissage et t=0,25..7,25 en validation, soit huit points chacun. Le cas pente 2 reste une constante : la pénalité de complexité peut dominer le petit gain de MSE, ce qui n’est pas corrigé ici. Il est conservé comme limite ; aucune tolérance n’est relâchée pour le masquer. Sur la démo quadratique par défaut, erreur max validation 0,01071926309712179 → 0,010719263097120901 : essentiellement l’arrondi, pas un progrès applicatif démontré.

Trois paires alternées démo et une paire par témoin, avec graine 42 : écart entre fitness et objectif de l’arbre égal à zéro dans tous les cas observés. Médianes processus complet 149,41 ms avant / 159,75 ms après. Petit échantillon bruité, aucun gain de vitesse annoncé. Temps de recherche séparés, formules et métriques des baselines dans gp-scaling-20261118.json. Processus complet : démarrage Node, contrôle d’intégrité des sources, recherche et écriture des rapports ; calcul isolé d’une formule, coûts Python/C, conversions et pipeline client non mesurés.

Limites : données synthétiques uniquement, une graine, échantillons finis ; pas de garantie continue, de nouvelle loi physique ni de validation client. Domaine CLI toujours |x|<=1e4 et |y|<=1e8 ; démo sur [-2,2], apprentissage [-1.975,1.9], un point test au-delà. La conversion en coefficients a,b et la simplification peuvent encore perdre des chiffres sur des cas extrêmes ; contrôle de finitude et score de l’arbre effectif conservés. Aucun candidat promu. Aucun visuel applicatif modifié ; tableau fondé sur le JSON vérifié, pas de capture d’interface requise.

Suite : qualifier des données réelles autorisées avec unités, partitions et tolérance métier ; issue #8 reste ouverte. Rétrospective locale session 13 : preuve avant/après et cas sans gain conservés, adaptation désactivée, signaux indéfinis null ; audit décennal non dû (dernier à la session 10).
