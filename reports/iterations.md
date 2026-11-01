# Premières itérations

1. Import SiLU/GELU figé avec empreintes et licence upstream ; aucun clone complet.
2. Interpréteur à closures : SiLU ~720 ns/élément ; GELU ~715 ns/élément lors du premier relevé.
3. Compilation AST autorisée : SiLU ~508 ns/élément ; GELU ~367 ns/élément au relevé suivant. Comparaison indicative entre passages courts, pas benchmark contrôlé.
4. Référence indépendante sur [-8,8] : erreur max SiLU nulle ; GELU 2,12e-7. Variantes fast : erreurs max ~0,1585 et ~0,1205 ; non activées.
5. Quatre tests passent en ~4 ms ; benchmark complet en une fraction de seconde. Résultats locaux détaillés : baseline.json.

Limites : aucune intégration navigateur/LLM/SIMD active ; performance end-to-end et parité aux exécutables upstream non encore mesurées.

## Benchmark de la découverte

Comparaison exécutée avec le même évaluateur vectoriel upstream, 4 096 points, préchauffage, ordre alterné, 21 répétitions de 8 passages. Script : benchmark_discovery.mjs ; résultats : discovery-speed.json.

- x*x → sq(x) : ~4,76 contre ~4,41 ns/élément, rapport 1,08×. Dispersion importante et même opération mathématique : aucun gain pratique démontré. Le contrôle JS direct utilise deux implémentations identiques et ne mesure que le bruit.
- Polynôme : ~1,18× mais erreur max 2,38 ; rejeté.
- sin(x) : ~2,57× mais erreur max 0,327 ; rejeté.

Conclusion : découverte effectivement branchée, mais aucune optimisation utile validée à ce stade. Les durées de recherche (~15 ms) ne sont pas des durées d'exécution des kernels. Les chiffres de coût modélisé restent distincts des mesures de temps.
