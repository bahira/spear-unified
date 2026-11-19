# Stabilité de la référence affine — 15 novembre 2026

Défaut reproduit : la référence affine partageait le calcul non centré de scaling du moteur GP. La soustraction de grandes sommes et un seuil absolu de variance pouvaient la réduire à une constante sur des x distincts et admissibles.

Correction limitée à cette référence : x centrés puis normalisés par leur écart maximal, covariance centrée avec y, prédiction dans ces coordonnées. Coefficients, centre, échelle et méthode exposés dans le rapport ; ajustement uniquement sur apprentissage. Le moteur vendored, son scaling GP, la recherche et la sélection restent inchangés.

Trois nouveaux tests : plage ordinaire, x proches de 9999 espacés de 1e-4, x proches de zéro espacés de 1e-9. Les deux derniers échouaient avant modification. 31 tests Python passent en 2,845 s ; 3 tests Node passent en 0,217 s. Erreur validation affine sur le cas décalé : 7,5e-4 avant / 5,3813e-12 après ; petite plage : 1,45e-8 / 2,2204e-16. Les données y sont affines synthétiques ; aucun jeu privé employé.

Trois paires alternées sur la démo par défaut, une paire sur chaque cas difficile : candidat exactement identique dans les cinq paires. Sur la démo, variation affine à l’arrondi près (erreur maximale 4,093364922268348 → 4,093364922268346). Médianes processus complet 160,26 → 146,17 ms : échantillon bruité, aucun gain de vitesse revendiqué. Temps de recherche séparés et mesures brutes dans affine-stability-20261115.json. Appels incluent démarrage Node, intégrité sources, recherche et rapports ; calcul de formule seul et coût Python/C non mesurés.

Limites : calcul double précision, sans certification de conditionnement ni garantie continue. Le scaling du GP conserve ses limites numériques historiques ; cette itération renforce seulement la baseline. Les contraintes existantes |x|<=1e4 et |y|<=1e8 restent appliquées. Pas de nouvelle loi physique, promotion automatique ou validation client. Aucun changement visuel : contrôle du rendu sans objet. Issue #8 ouverte pour données réelles et qualification.

## Rétrospective Triple Helix, session locale 10

Historique et état relus : signaux RFR/CSR/convergence/PHR indéfinis (null), aucune adaptation, essai, cooldown ou arête découverts à réévaluer. L’adaptation reste désactivée conformément à AGENTS.md et à l’issue #6 ; aucun ratio reconstruit a posteriori. Les preuves de cette itération couvrent échec avant correction, précision après correction, plage ordinaire, invariance du candidat et coût complet borné. Les drafts indépendantes ne sont pas considérées comme fusionnées ; aucune tâche réelle client terminée. Compteur de rétrospective remis à zéro ; pas de changement de paramètres.
