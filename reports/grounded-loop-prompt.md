# Grounded Loop dans les instructions permanentes

## Recommandation

Conserver un noyau court permanent : relier les affirmations importantes à une observation vérifiable, chercher une vérification adaptée, signaler les inconnues et corriger les conclusions lorsque les observations changent. Charger la procédure complète pour un audit, une décision coûteuse ou un résultat technique substantiel.

Source : `.agents/skills/triple-helix/SKILL.md`, boucle 3 « Operational (Grounded) ». Le document demande une source par artefact, des niveaux L0 à L3, un minimum L2 et des vérifications ponctuelles. Ses chiffres de bénéfice annoncés ne sont pas validés par une expérience sur ce projet.

## Interprétation utile

- Lire le fichier ou l'état courant avant d'affirmer ce qu'il contient.
- Exécuter un test pertinent lorsque l'affirmation est sur le comportement du code.
- Distinguer « une commande a été lancée », « elle a réussi » et « le résultat recherché a été vérifié ».
- Pour une mesure : préciser matériel, domaine, protocole, précision, baseline et limites.
- En cas de contradiction, changer la conclusion et, si nécessaire, le plan ; ne pas seulement reformuler l'affirmation initiale.

Une citation directe prouve ce qu'affirme une source, pas que l'affirmation est vraie. Un outil peut aussi produire une mesure erronée : examiner la méthode. Deux chemins utilisant le même moteur ne sont pas deux validations indépendantes. Un oracle indépendant peut vérifier une grille sans prouver un résultat sur tout le domaine continu.

## Application concrète dans SPEAR Unified

| Affirmation | Vérification requise | Résultat actuel |
|---|---|---|
| « Le dépôt est publié » | Réponse GitHub + commit distant | Vérifié pour les commits publiés |
| « La description GitHub est modifiée » | Relecture de la description après écriture | Faux : API refuse HTTP 403 ; texte seulement préparé |
| « Un kernel est plus rapide » | Benchmark reproductible et baseline forte, même précision | Plusieurs sondes seulement, pas de gain applicatif général |
| « Discovery généralise à des mesures » | Recherche depuis x/y sans formule cible, splits distincts | Démo synthétique disponible, pas de données métier |
| « La recherche évolutive apporte un avantage » | Comparaison aux modèles simples appropriés | Pas démontré sur la calibration quadratique synthétique |

## Noyau proposé

> Pour les affirmations qui déterminent une action ou une conclusion, vérifie la source ou le comportement actuel avec un contrôle adapté. Distingue faits observés, inférences, hypothèses et inconnues. Ne confonds pas citation et preuve, test local et validation générale. Si une preuve contredit le plan, corrige le plan. Rapporte brièvement les résultats, leur source et les limites qui changent la décision.

Ne pas lancer une recherche ou un test à chaque salutation ou chaque phrase. Ne pas imposer cinq probes identiques à tous les artefacts : dimensionner les vérifications selon le changement et les risques réels. Ne pas donner un pourcentage de grounding sans définir les affirmations comptées ni leur mode de validation.

## Coût et limites

Peut réduire les conclusions non étayées, les oublis d'état et les annonces de succès prématurées ; aucun taux d'amélioration n'est mesuré ici. Augmente parfois le temps et le nombre d'outils. L'objectif est une meilleure décision, pas un rituel de citation. Aucune modification du prompt système de la plateforme n'est effectuée ; le dépôt contient une méthode réutilisable et ses preuves.
