# SPEAR Unified — rapport d'intégration et expérimentation (2026-11-19)

## Périmètre réellement livré
- CLI Python avec SiLU/GELU et compilation AST bornée ; calcul et recherche de formules via Superspear.
- Validation de découverte sur points indépendants, bornes et milieux ; contrôle SHA-256 des sources du moteur.
- Recherche à partir d'échantillons x/y avec empreinte SHA-256 de l'entrée et suppression du chemin local dans le rapport.
- Benchmarks JSON/routage Python avec baseline mathématique directe, mesures alternées AB/BA.
- Expériences **optionnelles** C/ctypes : buffers, conversions JSON/listes, mélanges de domaines, contrôle de précision.
- CI Python 3.10/3.12, Node 24, recherche synthétique sur échantillons, sonde de précision native.

## Expérience intégrée dans la présente PR
La PR #26 ajoute la régression symbolique enrichie : stabilisation affine centrée/normalisée, comparaison à des références constante, affine et quadratique ajustées **uniquement sur l'entraînement**, erreurs sur train/validation/test, couverture des domaines et séparation des points à l'intérieur/extérieur du domaine d'entraînement. Neuf modules de tests ont été réintégrés depuis la PR #10. La CI ajoute une expérience bornée de latence CPU pour SiLU et GELU (257 échantillons, 3 répétitions, 1 échauffement) avec rapport JSON dans les logs Python 3.12.

## Interprétation et limites
- La comparaison référence mathématique vs Router n'est pas un duel de backends équivalents : le Router exécute aussi la sélection du registre et les métadonnées.
- Un candidat de recherche peut perdre contre une simple baseline quadratique : l'algorithme ne prouve ni supériorité, ni découverte d'une loi physique.
- Les points d'évaluation et tests de précision ne certifient pas une erreur bornée sur un domaine continu.
- La mesure CI utilise une machine virtuelle partagée : elle est une sonde reproductible, **pas** une preuve de performance sur le matériel du client.
- Les tests natifs ne constituent pas une activation du backend natif en production ; aucun gain d'accélération applicatif n'est démontré.

## Critères de passage à un pilote
1. CI complète verte, avec rapport de la sonde CPU conservé.
2. Comparaison d'au moins deux implémentations produisant la **même sortie** avec le **même contrat** de validation et de sérialisation.
3. Mesures répétées sur une machine dédiée ou un environnement stable, tailles de lots et distributions d'entrée représentatives.
4. Tolérance numérique définie, tests des bornes, fallback et cas extrêmes.
5. Déploiement opt-in avec possibilité de retour au backend de référence ; aucun auto-promotion.

## Traçabilité
- Dépôt : https://github.com/bahira/spear-unified
- Intégration principale : PR #26
- Travaux antérieurs : PR #16 (AST), #17–#19 (benchmarks), #20–#21 (provenance), #22 (smoke-test), #23–#24 (natif), #25 (README).
- PR #10 et #11 restent des branches historiques en conflit ; leur contenu doit être audité avant clôture.
