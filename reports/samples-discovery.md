# Régression symbolique depuis des mesures

Origine : synthetic_demo.

Candidat : ((1.748953 * (x)²) + 0.401007)
Référence affine : ((-0.130102 * x) + 2.728248)

train (32 points) : RMSE candidat 0.0059052, affine 2.0808, quadratique 0.0057741 ; erreur max candidat 0.0095591.
validation (21 points) : RMSE candidat 0.0056448, affine 2.0750, quadratique 0.0054139 ; erreur max candidat 0.010719.
test (23 points) : RMSE candidat 0.0060424, affine 2.0978, quadratique 0.0061476 ; erreur max candidat 0.0099889.

Recherche : 60.5 ms ; 1008 évaluations.

Evolution, least-squares affine scaling and candidate selection use training data only; validation and optional test are evaluated afterwards, never fitness or selection.

No clear GP advantage demonstrated: the train-fitted quadratic baseline is better on validation (RMSE 0.00541 vs GP 0.00564), while GP is only slightly better on the small test split (0.00604 vs 0.00615). Both recover the quadratic trend near the noise level.

A formula fitted to supplied observations; finite split checks do not establish causality, a new physical law, generalization beyond the sampled domain, or an execution speedup.

Démo synthétique clairement étiquetée : y = 1,75 x² + 0,4, bruit uniforme ±0,01. Les coefficients sont ajustés sur les observations et ne sont pas une validation scientifique.

Aucun candidat ajouté au registre. Aucune dépendance supplémentaire.
