# SPEAR Unified — offre, clients et prochaines étapes

Document de travail du 1er novembre 2026. Les tarifs ci-dessous sont des **prix de lancement proposés, à tester**, pas une étude des prix du marché ni des ventes déjà réalisées. Tous les montants sont en euros HT. Aucun client n'a été contacté dans le cadre de ce chantier.

## 1. Ce que l'on vend

**Une prestation d'optimisation CPU mesurée sur un calcul client, avec contraintes de qualité explicites.**

Promesse commerciale proposée : « Nous identifions un calcul coûteux dans votre pipeline, testons une optimisation sur vos données représentatives, et vous livrons une comparaison reproductible de vitesse, qualité et coût. Vous décidez de l'intégration à partir des résultats. »

On commence par du service : profilage, benchmark, preuve de concept et intégration. Le toolkit SPEAR est l'outil de production interne. On ne vend pas encore un moteur universel, une nouvelle loi physique, un remplacement de LLM, ni une baisse garantie de facture cloud.

## 2. Ce qui existe réellement

- Registre traçable SiLU/GELU, CLI Python/JSON, découverte symbolique Superspear avec petits budgets, graine fixe et timeout.
- Validation de candidats, domaine explicite, données de validation distinctes et contrôles indépendants ciblés.
- Benchmarks de vitesse et précision, comparaison avec une baseline simplifiée et rapports sauvegardés.
- GitHub privé, milestones/issues, objectif persistant et méthode Triple Helix.
- Tableau de bord local lisant les rapports ; pas encore hébergé ni synchronisé automatiquement avec GitHub.

**Preuves et limites :**

| Résultat | Ce qu'il démontre | Limite commerciale |
|---|---|---|
| C : Taylor 7 vs libm sin, environ 2,51×, erreur max 2,73e-6 sur [-1,1] | Un compromis numérique local peut améliorer le temps d'un kernel | Polynôme connu, microbenchmark d'une VM, pas une mesure du pipeline client ni de la facture |
| JS : Taylor 3 sur [-0.1,0.1], environ 1,21×, erreur max 8,33e-8 | Premier point de comparaison précision/vitesse | Bruit, performance dépendante du moteur et du domaine |
| exp(log(x)) découvert puis comparé à x | Nécessité d'une baseline forte | Le candidat perd face à x ; pas une optimisation à vendre |

Sources internes : [sonde native](reports/native-probe.md), [Pareto sinus](reports/pareto-sin.md), [validation corrigée](reports/validation-update.md). Les approximations Taylor sont classiques, pas découvertes par Superspear. Les adaptateurs navigateur, LLM et REA ne sont pas connectés. SpearVM n'est pas encore intégré au runtime.

## 3. Premier segment à cibler

**Équipes techniques ayant des calculs CPU répétés, un coût ou une latence déjà mesuré, et la capacité de fournir un jeu de test représentatif.**

Commencer par des simulations ou traitements de signaux non critiques, ou des services de calcul par lots. L'objectif est un calcul dont les entrées, le domaine et la tolérance peuvent être explicités. Les petites équipes avec un CTO accessible et un pipeline maîtrisé peuvent décider plus vite qu'un grand compte ; hypothèse à tester en entretien.

| Segment / usage | Problème à qualifier | Premier livrable utile | Décideur possible |
|---|---|---|---|
| SaaS de traitement de signaux ou séries temporelles | Calculs numériques répétés, CPU saturé | Benchmark d'un lot complet avec contrôle de qualité | CTO, lead backend |
| Simulation ou graphisme | Fonctions coûteuses sur un domaine borné | Variante précise/rapide et validation de l'effet final | Lead simulation, graphics engineer |
| Petits modèles ML sur CPU | Activation ou opérations non fusionnées coûteuses | Profilage du modèle complet puis test d'un kernel | ML engineer, responsable plateforme |
| Éditeur embarqué x86 compatible | Budget de calcul contraint | Kernel C testé sur le matériel cible | Responsable logiciel embarqué |

Ne pas commencer par une équipe principalement GPU sans point chaud CPU établi, par des applications dominées par les appels réseau, ou par une équipe dont le calcul est déjà négligeable. Les cas médicaux, sûreté et fonctions exigeant une exactitude stricte ne sont pas la première cible d'un pilote approximatif.

## 4. Offres et tickets proposés

### Offre A — diagnostic ciblé : 1 500 € HT

- Périmètre : un pipeline ou une fonction, un environnement matériel, un jeu de données représentatif.
- Effort visé : 1 à 2 jours de travail après réception des éléments ; délai de livraison convenu à la qualification.
- Livrables : baseline, localisation du coût, contraintes numériques, pistes classées, rapport go/no-go et protocole reproductible.
- Résultat possible : pas de gain économiquement intéressant. L'audit reste un livrable payé ; on n'invente pas un ROI pour vendre la suite.
- Le périmètre exclut le déploiement en production et une réécriture générale.

### Offre B — pilote d'optimisation : 3 500 € HT additionnels

- Démarre uniquement si le diagnostic identifie une piste et un protocole acceptés.
- Périmètre : un point chaud, jusqu'à trois variantes, une famille de matériel et des jeux de validation convenus.
- Effort visé : 3 à 5 jours. Si la complexité dépasse le forfait, nouveau devis avant travaux supplémentaires.
- Livrables : code prototype, tests, mesure du pipeline avant/après, dispersion, précision et domaine, limites et recommandation.
- Le client paie une expérimentation bornée ; aucun pourcentage d'accélération garanti avant mesure.

### Offre C — intégration : à partir de 6 000 € HT

- Devis après pilote ; exemple : 6 000 à 12 000 € HT pour une intégration circonscrite, selon packaging, CI, plateformes et validation.
- Livrables à contractualiser : API adaptée, tests de non-régression, packaging, documentation et procédure de retour arrière.
- L'effort et le calendrier sont estimés sur le code réel. Le prix d'appel ne couvre pas toutes les infrastructures ni tous les matériels.

### Support optionnel : 500 à 1 500 € HT / mois

À proposer après intégration, avec un volume de temps et des tâches explicitement inclus. Exemple de départ : 500 € pour au plus une demi-journée planifiée par mois ; incidents, SLA et astreinte à chiffrer séparément. Éviter le support illimité.

**Conditions proposées à discuter :** forfait et critères signés ; diagnostic payé à la commande ; pilote et intégration avec acompte de 50 %, solde à livraison des éléments convenus. Les critères de livraison ne doivent pas dépendre d'un gain qui n'a pas été démontré. Préciser droits sur le code client, composants open source et outils réutilisables ; conserver les mentions des licences MIT importées.

## 5. Combien cela peut rapporter

Ce sont des scénarios de **chiffre d'affaires**, pas du bénéfice ni un revenu net personnel.

| Scénario illustratif | Calcul | CA HT |
|---|---|---:|
| Un diagnostic | 1 × 1 500 | 1 500 € |
| Diagnostic + pilote chez un client | 1 500 + 3 500 | 5 000 € |
| Parcours complet au prix d'intégration de départ | 1 500 + 3 500 + 6 000 | 11 000 € |
| Exemple de mois avec deux diagnostics et un pilote | 2 × 1 500 + 3 500 | 6 500 € |

Les ventes peuvent aussi être nulles. Un pilote est additionnel au diagnostic, pas automatiquement vendu. Le mois à 6 500 € représente environ 5 à 9 jours de livraison selon le périmètre, auxquels s'ajoutent prospection, réunions, administratif et éventuelles reprises. Aucune conversion n'est acquise.

Calcul de contribution par mission : prix HT moins sous-traitance, infrastructure, licences éventuelles et autres coûts directs. Pour connaître le revenu réel, déduire aussi acquisition client, temps non facturé, frais fixes, cotisations et fiscalité selon la structure. Ne pas traiter tout le CA comme de l'« oseille dans la poche ».

## 6. Comment démontrer le ROI client

Partir du pipeline complet et du coût pertinent : CPU-heure facturé, machine mobilisée, débit ou latence qui débloque un usage. Une accélération peut libérer de la capacité sans diminuer une facture fixe.

Loi d'Amdahl : speedup total = 1 / ((1-p) + p/s), avec p fraction du temps passée dans le calcul optimisé et s son accélération. Par exemple p=20 % et s=2,5 donnent environ 1,14× au total, soit environ 12 % de temps économisé — pas 60 %.

Exemple purement illustratif : si une dépense variable réellement évitable est de 5 000 €/mois et baisse de 10 %, l'économie est de 500 €/mois. Un pilote à 3 500 € serait amorti en 7 mois, hors diagnostic, intégration et support. Un parcours total à 11 000 € serait amorti en 22 mois dans cette hypothèse. Ce cas peut être trop faible pour le client : qualifier avant de vendre l'intégration. Si le bénéfice porte sur la latence, chiffrer sa valeur avec le client plutôt que d'inventer des économies cloud.

## 7. Trouver les premiers clients

### Recherche manuelle, ciblée

1. Réseau existant : CTO, développeurs, équipes data et simulation ; demander un entretien de qualification sur un problème réel.
2. LinkedIn : chercher des fonctions précises et des signaux publics (performance CPU, batch lent, simulation, inférence CPU), puis sélectionner les entreprises une par une.
3. Communautés techniques : partager un benchmark reproductible et ses limites, répondre aux besoins exprimés, inviter à un diagnostic lorsque le problème correspond.
4. Partenaires : agences backend/data et consultants cloud qui constatent un point chaud de calcul hors de leur périmètre.

GitHub sert à identifier une technologie ou publier une démonstration, pas à déduire le budget ou les coordonnées personnelles d'un contributeur. Le dépôt projet reste privé ; préparer une démo distincte expurgée avant tout partage externe.

### Questions de qualification en 20 minutes

- Quel calcul est lent, à quelle fréquence et sur quel matériel ?
- Quelle fraction du temps total lui revient selon le profilage actuel ?
- Quelle métrique compte : latence, débit, capacité, coût variable ?
- Quelle erreur est acceptable et quel effet final serait inacceptable ?
- Existe-t-il un échantillon représentatif et un environnement reproductible ?
- Qui peut décider, quel budget et quelle échéance ?

Si le problème est surtout I/O, si les données ne peuvent être fournies, ou si le potentiel économique est insuffisant : proposer une autre piste ou ne pas vendre ce diagnostic.

### Exemple de message à personnaliser — brouillon, non envoyé

« Bonjour [Prénom], vous travaillez sur [signal public précis]. Nous développons une méthode pour comparer des optimisations CPU avec un budget d'erreur explicite et des benchmarks reproductibles. Est-ce qu'un calcul répété limite aujourd'hui votre débit ou votre latence ? Je vous propose 20 minutes pour voir si un diagnostic ciblé aurait du sens. Si oui, le forfait de lancement est de 1 500 € HT pour un périmètre défini et un rapport go/no-go. »

Ne pas joindre de données privées ni présenter le microbenchmark 2,51× comme une garantie client. Aucun message n'est envoyé automatiquement.

## 8. Plan d'action sur deux semaines — objectif de travail, pas prévision

| Étape | Action | Livrable / critère |
|---|---|---|
| 1 | Choisir un segment initial et une douleur | Une phrase d'offre et 3 critères de qualification |
| 2 | Préparer une démonstration partageable | Benchmark de pipeline complet, précision et limites visibles ; aucune donnée privée |
| 3 | Préparer fiche commerciale et exemple de rapport | Offre A claire, périmètre, prix et go/no-go |
| 4 | Constituer une liste de 20 entreprises qualifiées | Source publique, signal de besoin, rôle cible, raison du fit |
| 5 | Contacter personnellement une première petite vague après validation des destinataires | Messages adaptés ; suivre les réponses, pas le volume seul |
| 6 | Réaliser les entretiens | Consigner le problème, le coût, le budget et les objections |
| 7 | Proposer un diagnostic payé si le besoin est confirmé | Accord sur données, périmètre et livrable |
| 8 | Ajuster l'offre selon les faits | Garder un segment précis ; ne pas lancer un SaaS faute de réponses |

Cibles d'activité indicatives : 20 comptes recherchés, 5 entretiens souhaités, 1 diagnostic payé recherché. Il ne s'agit ni de taux de conversion mesurés ni de résultats promis. Le temps nécessaire dépend des réponses et de l'accès aux données.

## 9. Next steps techniques et commerciaux

1. **Priorité immédiate : un vrai cas de bout en bout.** Choisir un calcul représentatif, une baseline forte, une tolérance et une mesure indépendante. Pas seulement un sinus isolé.
2. Ajouter le coût des appels et de l'intégration, les cas hors domaine et le comportement de repli vers la référence.
3. Conserver les résultats négatifs : un candidat plus lent ou trop imprécis ne part pas en production.
4. Finaliser la fiche d'offre et l'exemple de rapport ; valider le prix sur des entretiens et des missions payées.
5. Recruter un premier pilote via un problème vérifié. Après plusieurs cas similaires, décider si un SDK ou un service hébergé a une demande réelle.

Le navigateur/Pomerado, REA et le routage LLM restent des pistes séparées. Ne pas les ajouter à l'offre CPU tant qu'ils ne répondent pas au besoin du pilote ; cela évite une offre confuse et des dépendances inutiles.

## 10. Suivi

Repo privé : https://github.com/bahira/spear-unified. Le suivi technique reste dans les issues/milestones. Les prix et scénarios de ce document doivent être révisés à partir des objections, du temps réellement passé, des coûts et des ventes constatées.

La description GitHub reste non modifiée : le jeton refuse ce réglage. Texte proposé dans github-description.txt. Les fichiers de documentation peuvent être mis à jour et poussés normalement.
