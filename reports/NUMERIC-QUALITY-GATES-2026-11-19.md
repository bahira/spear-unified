# Numeric safety gates from historical SPEAR papers — 2026-11-19

The historical SPEAR reports flagged float32 drift, inverse-composition errors and extrapolation risk. `spear/quality.py` provides **offline checks** without changing any production runtime selection. Source records are still SHA-256 pinned.

## Implementation

- `audit_ledger(kernel, abs_tol=..., rel_tol=..., domain=..., probes=..., arithmetic=...)` compares the pinned SiLU/GELU ledger candidate against independent `math` reference values on a bounded grid (including endpoints).
- Arithmetic modes: `python-f64` (existing Python runtime) and `emulated-f32-step-rounded` (round every expression-node result to IEEE 754 binary32 with Python struct).
- `audit_composition(first, second, abs_tol=..., domain=...)` rejects inverse/forward pairs whose composed result departs from identity or target on the tested domain.
- Strict input validation: finite domain, error budgets and outputs; max 8193 probes, AST complexity limits inherited from core; error budgets fail closed.
- Every output explicitly states `backend_promoted=false`, `samples_certify_domain=false`. Float32 emulation explicitly states `native_parity_verified=false`. Ledger hash and commit included for provenance.
- No package or compiler dependencies.

## Examples

```bash
python -m scripts.audit_precision --kernel gelu --dtype python-f64 --abs-tol 0.001 --probes 1025
python -m scripts.audit_precision --kernel silu --dtype emulated-f32-step-rounded --abs-tol 0.01 --probes 257
python -m unittest tests.test_quality -v
```

CLI returns exit code 0 on pass, 2 on budget exceed. It rejects malformed parameters with nonzero exit. The tolerances in these example commands are **illustrative**, not approved production acceptance thresholds.

## What this does NOT verify

- This is finite sampling, not a uniform mathematical interval proof.
- Python-step-rounded float32 does not exactly model native C's FMA, vector transcendental implementations, subnormals, overflow policy, compiler optimizations or ABI.
- A passing numerical gate is not proof of performance, model-level task quality, robustness under distribution shift or security.
- No automatic runtime backend activation. Native CPU/WASM parity and model-level quality must be checked separately.
