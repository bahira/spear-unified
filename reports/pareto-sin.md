# Compromis vitesse/précision pour sin(x)

**Approximations Taylor connues, pas nouvelles lois ni candidats découverts.** Script : `scripts/pareto-sin.mjs`. Mesures locales Node 24.19.0 Linux x64, 4 097 valeurs incluant les bornes, allocations identiques, 40 préchauffages, 31 répétitions ×16 passages, ordre tournant et inversé. Temps en ns/élément ; dispersion p10–p90 dans le JSON.

| Domaine | Formule | Erreur absolue max | ns/élément médian | Rapport vs Math.sin |
|---|---|---:|---:|---:|
| [-0.1,0.1] | Math.sin(x) | 0 (référence) | 14.56 | 1.00× |
| [-0.1,0.1] | x | 1.67e-4 | 8.91 | 1.64× |
| [-0.1,0.1] | x(1−x²/6) | 8.33e-8 | 12.05 | 1.21× |
| [-0.1,0.1] | x(1−x²/6+x⁴/120) | 1.98e-11 | 12.22 | 1.19× |
| [-1,1] | Math.sin(x) | 0 (référence) | 15.41 | 1.00× |
| [-1,1] | x | 0.1585 | 8.67 | 1.78× |
| [-1,1] | x(1−x²/6) | 8.14e-3 | 11.86 | 1.30× |
| [-1,1] | x(1−x²/6+x⁴/120) | 1.96e-4 | 12.25 | 1.26× |

## Décision pratique

- Budget erreur **1e-4**, domaine **[-0.1,0.1]** : Taylor degré 3 est un candidat utile ; ~1.21× sur cette exécution, erreur 8.33e-8. La variante linéaire échoue au seuil.
- Budget erreur **1e-4**, domaine **[-1,1]** : aucun des trois polynômes ne passe ; conserver Math.sin.
- Si erreur tolérée **2e-4** sur [-1,1] : Taylor degré 5 passe de justesse sur la grille ; ne pas transformer ce probe en certification globale.
- Degré 3 et 5 ont des temps très proches et des dispersions superposées : ne pas présenter leur ordre de vitesse comme établi. Le choix dépend surtout de la précision demandée.

La référence est Math.sin, pas une vérité d'arrondi exacte. Ces erreurs sont des mesures sur grille et bornes, pas une preuve de borne continue. Un gros outlier sur la référence du petit domaine et un autre sur le degré 5 rappellent le bruit de la VM ; les médianes limitent leur influence. Aucun gain end-to-end ni natif/SIMD revendiqué. Aucune modification au runtime ou au registre.
