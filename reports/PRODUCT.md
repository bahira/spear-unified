# Goal et piste produit

## Promesse à vérifier
Réduire la latence ou le coût CPU d'un calcul réel, avec un budget d'erreur explicite, un domaine valide et des mesures reproductibles. La recherche symbolique propose des candidats ; une validation indépendante et une baseline forte décident de leur intérêt. Ni nouvelle loi physique, ni remplacement général d'un LLM.

## État
Recherche Superspear bornée, registre figé SiLU/GELU, CLI Python/JSON, comparaison vitesse/précision, tests, Triple Helix et suivi GitHub. Les adaptateurs navigateur, LLM et REA ne sont pas connectés. Une sonde C Taylor ordre 7 sur [-1,1] mesure ~2,51× vs libm sin pour erreur max ~2,73e-6 ; approximation connue, microbenchmark local, sans coût Python/C ni mesure applicative. Le candidat découvert pour exp(log(x)) perd face à la simplification connue x.

## Use cases prioritaires
1. Simulation, graphiques ou traitement de signaux : approximations de fonctions sur domaines bornés, après définition du budget d'erreur.
2. Calcul par lots sur CPU : fusion et vectorisation lorsque le profil applicatif montre un point chaud. Gain à mesurer en situation réelle.
3. Petits modèles ML sur CPU : noyaux d'activation et opérations fusionnées ; vérifier la qualité du modèle, pas seulement l'erreur du kernel.
4. Automatisation répétitive via Pomerado : module futur distinct. Rejeu potentiellement moins coûteux qu'une exploration répétée ; pas encore intégré ni tarifé.

## Monétisation, hypothèses non validées
Commencer par une prestation d'audit/benchmark et preuve de concept sur un calcul client. Livrable : coût initial, contraintes de qualité, gain reproductible ou constat d'absence de gain. Puis vendre intégration, support et SDK si plusieurs cas clients convergent. SaaS de benchmarks en option après validation du besoin, sans construire l'infrastructure avant les premiers utilisateurs.

Le code provenant de dépôts MIT reste soumis à ses mentions de licence ; la valeur payante peut résider dans le service, l'intégration, le support et l'expérience produit. Aucun chiffre de revenus ou économie client n'est établi.

## Prochain jalon produit
Un calcul utile choisi avec un utilisateur pilote, profilé avant/après dans son application, qualité vérifiée et coût total mesuré. Seuil de succès à convenir avec le pilote. Un microbenchmark isolé ne suffit pas à démontrer une économie de facture cloud.
