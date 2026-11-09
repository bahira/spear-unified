# Goal: unified, measured, lightweight SPEAR toolkit

Build a nonredundant pipeline: discover formulas with Superspear, validate precision and domain, select a measured execution backend, and expose explicit routing. Keep browser automation, LLM and REA investigation as optional adapters. Preserve reproducibility and fast iterations on modest hardware.

## Done
- Pinned SiLU/GELU source records and executable Python runtime.
- Bounded Superspear evolutionary search with deterministic seed and holdout; domain endpoints and interval midpoints participate in acceptance (draft PR #9, latest iteration 2026-11-09); no continuous-domain certificate.
- Tests passing; reports distinguish modelled cost, search time and execution speed.
- Parallel investigation and benchmark audit produced evidence in reports/.

## Next, in order
1. DONE: benchmark domains, finite metrics, vendor checksums and total subprocess timing.
2. DONE: independent identity validation including endpoints; candidate loses to x and is not promoted. See reports/validation-update.md.
3. Explore precision/speed Pareto points with explicit tolerances and end-to-end measurements.
4. Evaluate one optional native backend; keep only measured benefits.
5. Add explicit browser/LLM/REA adapters after a concrete use case; avoid installing whole stacks prematurely.

## Completion criteria
Reproducible validated candidate, fair comparison to a strong baseline, recorded limitations, short tests and a usable CLI. No global speedup claim without evidence. Required tasks remain tracked even when deferred.
