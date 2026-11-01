# Goal: unified, measured, lightweight SPEAR toolkit

Build a nonredundant pipeline: discover formulas with Superspear, validate precision and domain, select a measured execution backend, and expose explicit routing. Keep browser automation, LLM and REA investigation as optional adapters. Preserve reproducibility and fast iterations on modest hardware.

## Done
- Pinned SiLU/GELU source records and executable Python runtime.
- Bounded Superspear evolutionary search with deterministic seed and holdout.
- Nine tests passing; reports distinguish modelled cost, search time and execution speed.
- Parallel investigation and benchmark audit produced evidence in reports/.

## Next, in order
1. Correct benchmark domain selection and reject nonfinite metrics; measure subprocess overhead separately.
2. Validate identity candidate exp(log(x)) on [0.1,2] against simplified baseline x, including endpoints and independent oracle. Existing speedup is against an unsimplified target and is not a new mathematical discovery.
3. Explore precision/speed Pareto points with explicit tolerances and end-to-end measurements.
4. Evaluate one optional native backend; keep only measured benefits.
5. Add explicit browser/LLM/REA adapters after a concrete use case; avoid installing whole stacks prematurely.

## Completion criteria
Reproducible validated candidate, fair comparison to a strong baseline, recorded limitations, short tests and a usable CLI. No global speedup claim without evidence. Required tasks remain tracked even when deferred.
