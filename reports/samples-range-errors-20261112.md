# Erreurs par plage — 12 novembre 2026

Une moyenne globale pouvait masquer les erreurs d’extrapolation. `range_metrics` sépare désormais `inside_training` (bornes incluses) et `outside_training`, pour le candidat et les références affine/quadratique. Groupes vides : `null`. Ajustement et sélection inchangés ; aucune promotion.

Validation : 3 nouveaux tests échouaient avant modification ; 25 tests Python et 3 tests Node passent après. Le test contradictoire ajoute 1000 aux observations hors plage de validation : les modèles ajustés restent identiques. Les MSE pondérées des groupes reconstruisent la MSE globale.

Trois paires alternées avant/après sur la démo synthétique : candidat et métriques globales exactement inchangés. Médianes processus complet : base 162.06 ms ; modifié 167.07 ms. Ce petit échantillon bruité ne démontre aucun gain de vitesse. Les temps de recherche et détails bruts figurent dans le JSON voisin.

Domaine d’apprentissage : [-1.975, 1.9]. Le test synthétique contient 22 points dans la plage et un point hors plage : une seule observation extrapolée ne permet aucune conclusion générale. Aucune donnée réelle disponible/validée pour cette itération. Aucun certificat continu, causalité ou nouvelle loi physique. Aucun changement visuel ; vérification de rendu sans objet.
