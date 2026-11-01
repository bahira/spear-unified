# Sonde native C

Résultat : 2.51× dans ce microbenchmark, erreur maximale 2.73e-06 sur [-1,1].

Polynôme de Taylor classique d’ordre 7, pas une découverte Superspear. Référence libm sin(double), grille de 65 537 points incluant les bornes. Deux fonctions noinline, même coût de réduction, somme consommée dans une variable volatile, ordre alterné, médiane de neuf répétitions après préchauffage. Compilation -O2 sans fast-math et contraction FMA désactivée.

La mesure ne comprend pas un passage Python/C ni le routage et ne justifie pas un remplacement général de sin. Elle ne valide que la grille et le domaine annoncés, sur cette VM. Aucun fichier du runtime modifié.
