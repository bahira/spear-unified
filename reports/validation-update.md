# Validation et benchmark corrigés

- Chaque candidat utilise son domaine, bornes incluses. NaN/Infinity et métriques non finies sont rejetés.
- Les temps appariés sont enregistrés ; recherche et coût total du subprocess sont distincts.
- Les fichiers du moteur sont contrôlés par SHA-256 avant la recherche.
- Le candidat exp(log(x)) sur [0.1,2] est validé indépendamment en Python sur 10001 points, bornes incluses : erreur max 5.55e-17.
- Recherche + holdout : 50.3 ms ; subprocess complet : 140.4 ms.
- Évaluateur Node : 3.72× contre la cible non simplifiée, mais seulement 0.038× contre x avec copie de sortie. Le candidat est donc plus lent que la baseline forte et n'est pas promu.

Ces mesures sont une sonde locale bruitée, pas un résultat C/SIMD. L'identité est connue ; aucune nouvelle loi mathématique découverte.

GitHub : code, README et issues accessibles. Modification de la description du dépôt refusée par le jeton (HTTP 403 Resource not accessible by integration). Le texte proposé est enregistré dans github-description.txt.
