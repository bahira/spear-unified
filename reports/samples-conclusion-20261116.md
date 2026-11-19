# Conclusion calculée depuis les mesures — 16 novembre 2026

Défaut : le rapport de démo synthétique annonçait des RMSE et une tendance quadratique écrites en dur. Une évolution du générateur ou de la recherche pouvait laisser ces affirmations inchangées malgré des mesures différentes. Pour les données fournies, la conclusion ne présentait aucune comparaison numérique courante.

La conclusion est désormais dérivée des MSE/RMSE courantes de validation et, si présente, de test. Elle compare descriptivement le candidat à la référence quadratique ajustée uniquement sur apprentissage. Aucun classement ne prouve une significativité statistique, un avantage GP général, une précision continue ou un gain d’exécution. Une partition absente n’est pas inventée. La même conclusion est écrite dans JSON, Markdown et stdout.

Trois tests ajoutés échouaient avant modification : démo actuelle, générateur synthétique changé dans une copie temporaire, données fournies sans test. Après correction : 34 tests Python passent en 3,364 s et 3 tests Node en 0,178 s. Tous les essais utilisent des données synthétiques, sans collecte extérieure ni installation.

Trois paires alternées sur la démo : candidat, erreurs globales/par plage et comparaisons de référence exactement identiques avant/après. Médianes processus complet 158,98 ms avant / 153,70 ms après ; variation bruitée, aucun gain revendiqué. Détails et temps de recherche séparés dans samples-conclusion-20261116.json. Ces temps incluent démarrage Node, vérification de sources, recherche et écriture des rapports ; ils ne mesurent pas l’exécution isolée d’une formule ni la frontière Python/C.

RMSE validation : candidat 0,00564484 contre quadratique 0,00541393 ; test : 0,00604242 contre 0,00614756. Conclusion strictement descriptive. Domaine synthétique x généré dans [-2,2], apprentissage [-1.975,1.9], un point test hors plage ; aucune certification continue ni validation client. Ni tolérances, ni recherche, ni scaling GP, ni registre modifiés. Aucun changement visuel : vérification de rendu sans objet.

Prochaine étape : stabilité numérique du scaling GP (limitation encore ouverte), ou données réelles autorisées. Issue #8 reste ouverte. Rétrospective locale session 11 : aucune adaptation, signaux indéfinis conservés null ; rétrospective décennale déjà faite à la session 10.
