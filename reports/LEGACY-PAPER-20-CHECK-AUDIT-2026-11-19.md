# Historical SPEAR papers: 20-check evidence audit — 2026-11-19

**Scope:** source review of the user's own earlier manuscript `bahira/superspear/paper/main.tex`, revised draft `PAPER.md`, and four historical experiment reports; comparison to current SPEAR Unified GOAL. **This is a document/source audit, not a new independent performance run.** A checked item means its *source was inspected*, not that the numerical result was independently reproduced.

## Checkpoint 1 — 20 completed source-review checks

| # | Checked item | Source finding | Decision |
|---:|---|---|---|
| 1 | Original manuscript located | `paper/main.tex`, dated August 2026 | Cite as historical manuscript, not peer-reviewed publication |
| 2 | Revised draft located | `PAPER.md` explicitly marks [MEASURE] gaps | Use revised text as editorial warning, not independent proof |
| 3 | Search objectives | NSGA-II on train MSE and modeled ALU/SFU cost | Reuse multiobjective framing; add measured wall clock and p95 |
| 4 | Search-space priors | Padé, rsqrt, reciprocal powers and scaffolds | Reuse shape-only priors, avoid test-set leakage |
| 5 | Four difficulty regimes | R1–R4 classification of tasks | Use to route search budgets, validate on held-out tasks |
| 6 | Dual operating points | precise vs fast formula | Expose explicit precision budget, never automatic promotion |
| 7 | Protected division | denominator floor ±1e-4 and output clamp ±1e4 | Require exact semantic parity and independent domain tests |
| 8 | Cross-backend export | JS/WASM/C/PyTorch parity claimed | Re-run on the actual target/compiler/ABI |
| 9 | Reproducibility | seeds, AST, iterations, cost in ledger | Reuse SHA-256 provenance and replayable experiment records |
| 10 | Old modeled performance | ALU/SFU estimates used as speed proxies | Reject as commercial speed evidence |
| 11 | Cost calibration negative | median abs log ratio 0.097→0.177 when calibrated from serial op chains | Benchmark whole kernels and pipeline, not isolated op latency |
| 12 | f32 numerical drift | 40 champions reviewed; 30 f64-exact not f32-exact | Gate at deployed dtype and compiler flags |
| 13 | Inverse composition failure | sigmoid/logit inverse pair max error ~1.628 on historical sweep | Add composition tests; reject unsafe inverse pairs |
| 14 | Lambert W extrapolation | clamped form produces extreme out-of-range values | Strict domain bounds, OOD fallback |
| 15 | Other extrapolation | EMA, sRGB and Huber report off-domain oddities | Boundary and property-based tests |
| 16 | Fast-slot performance | Historical 40 resolvable; 32 ≥1.2× measured *kernel-only* speed | Treat as candidates, not end-to-end wins |
| 17 | Fast-slot accuracy cost | Example GELU fast MSE 2.97e-3; SiLU fast MSE 7.34e-3 | Do not deploy without task-specific error budget |
| 18 | Framework negative | Revised draft reports PyTorch GELU swap +0.56 perplexity, −9.2% throughput | Prioritize raw WASM/embedded or fused specialized execution |
| 19 | ORT negative | Revised draft: ORT fused erf-GELU 10.2 ns/elem vs algebraic 20.3 | Do not claim speedup against optimized framework |
| 20 | Contradictory/withdrawn claims | Original TeX abstract retains ×1840 iterative solver headline; revised PAPER.md explicitly withdraws Gaussian CDF ×1840 strawman | **Block reuse of stale TeX performance claims**; reconcile source-of-truth before publishing |

## What is actually reusable

**P0 — adopt methodology and checks, not historical headline numbers:**
- Multi-objective search for accuracy, *measured* speed, and complexity; stratified by architecture and domain.
- Precise/fast slots with explicit, independently checked error budgets and fallbacks.
- Strict C/WASM/JS parity, f32 vs f64 audits, inverse-composition and out-of-domain probes.
- Model cost as a search heuristic only; measured matched-contract application benchmark is the promotion authority.

**P1 — candidate niches:**
- Small repeated inference workloads with prepacked weights and fused operations (SpearVM, TensorFold).
- Browser/WASM or embedded workloads with expensive transcendental operations, if a real adopter exists.
- Search seeding with scaffold *shapes*, preserving train/test isolation.

**No-go without further evidence:** generic acceleration of PyTorch/ONNX, claims based on cost models or Monte-Carlo strawmen, unconstrained approximate GELU/SiLU in precision-sensitive LLM inference.

## Proposed falsifiable experiment

1. Fixed realistic model and workload, exact reference + optimized baseline (PyTorch CPU, ONNX Runtime, NumPy/BLAS as appropriate).
2. Compare SpearVM packed MLP and TensorFold fused SwiGLU / int8 GEMV with identical inputs and outputs.
3. Track setup/packing cost, input conversion, inference, output transfer, p50/p95 latency and peak RSS; >=30 paired AB/BA samples.
4. Gate maximum absolute and relative error, output semantics, f32 precision, domain and model-level quality.
5. Promote only on >=20% full-pipeline latency reduction OR >=25% throughput improvement with no p95 or quality regression, and a realistic reuse/payback calculation.

## Historical source links

- https://github.com/bahira/superspear/blob/main/paper/main.tex
- https://github.com/bahira/superspear/blob/main/PAPER.md
- https://github.com/bahira/superspear/blob/main/REPORTS/cost-model-calibration.md
- https://github.com/bahira/superspear/blob/main/REPORTS/f32-degradation.md
- https://github.com/bahira/superspear/blob/main/REPORTS/composition-audit.md
- https://github.com/bahira/superspear/blob/main/REPORTS/fast-slots-bench.md

## Verification limits and visual evidence

The 20 checks above are completed **source inspections**; they are not 20 implemented features, 20 new benchmarks or independently validated scientific claims. No original benchmark screenshot was captured from a running application in this audit. A plot based on historic reported data must be labeled as historic and not a new experiment. No live visual UI changed, so no product UI screenshot is available.
