# SPEAR Unified — first-principles asymmetric-edge review (2026-11-19)

## The actual problem

An approximation engine is not valuable by itself. Value comes from reducing the **total cost of a repeated, economically important workload** under an explicit error and reliability budget. Current evidence is negative for the existing Python ledger: the same-contract pilot benchmark on CI found ledger 1.40–2.58× slower than the direct math reference (see [measured results](PILOT-CPU-BENCHMARK-2026-11-19.md)). Do not describe this as acceleration.

### Unit economics

For N invocations of a candidate specialization, total savings are:

`S(N) = N * (T_baseline - T_candidate) - T_discovery - T_compile - T_validation - T_integration - T_maintenance`

This is a *model*, not a measurement. The breakeven call count is `N > fixed_cost / per_call_saving` only if the per-call saving is positive. If `T_candidate >= T_baseline`, amortization cannot rescue the optimization. For throughput-sensitive workloads, memory traffic, vectorization, conversion, cache, allocation and batching are part of `T_candidate`.

### Where asymmetric advantage could come from

1. **Work elimination and fusion** (highest-priority hypothesis): fuse a domain-specific sequence of operations into a single vectorized kernel, removing intermediate allocations, Python loops, conversions and repeated dispatch. Benchmark against a strong optimized baseline (NumPy/PyTorch/ONNX Runtime or equivalent, not just Python scalar math). Advantage is only possible where the baseline does not already fuse the same operations.
2. **Constrained-domain specialization**: specialize a frequently repeated transformation to an observed bounded input distribution and permitted error budget, with robust out-of-domain fallback. This is a candidate moat only if the specialization remains correct under distribution shift and cannot be matched trivially by standard compiler optimizations.
3. **Amortized compilation/caching**: pay a one-time discovery and verification cost for repeated execution. Track actual reuse counts, cache invalidation, recompilation and maintenance.
4. **Edge/offline deployment**: WASM or native CPU can matter if target users cannot use GPUs and latency, energy, binary size or privacy dominate. WASM is a deployment choice, not an assumed performance advantage.

### What is NOT an edge

- Symbolic regression alone: established compilers, polynomial approximations, vector math libraries and vendor intrinsics already exist.
- Faster scalar sin/GELU vs a slow Python implementation: unfair baseline, often irrelevant to real workloads.
- A native C bridge when list/JSON conversion dominates.
- Speedup extrapolated from synthetic CI microbenchmarks.
- General-purpose browser/LLM agent orchestration; it is orthogonal to CPU math optimization.

## Decision matrix (hypotheses, not claims)

| Candidate | Leverage | Differentiation | Execution cost | Decision |
| --- | --- | --- | --- | --- |
| Domain-specific fused CPU kernels | Potentially high for repeated batch jobs | Medium if workload-specific and reproducibly validated | Medium | **Primary experiment** |
| Approximate scalar SiLU/GELU Python ledger | Measured negative | Low | Low | **Stop optimizing as a product** |
| Automatic symbolic discovery for constrained transforms | Unproven, can support primary experiment | Medium if strong independent validation | High | Keep as offline R&D tool |
| Generic WASM math runtime | Unknown | Low | Medium | Defer until browser customer/workload |
| Generic LLM/browser adapter | Unrelated to performance thesis | Low | High | Defer |

## Falsifiable 2-stage experiment

**Stage A: baseline and cost decomposition.** Pick one actual repeated workload and collect input distributions and shape (e.g. CPU inference post-processing, image/pixel transformation or numerical ETL). Record machine, compiler flags, runtime versions, p50/p95 latency, throughput, allocations, energy if available, and accuracy. Compare a plain Python implementation, a properly vectorized library baseline, and one fused C candidate using *identical* input/output contract and serialization. Include data movement and startup separately.

**Stage B: constrained specialization.** If fusion is already beneficial, introduce one approximation on a bounded domain. Compare exact fused C vs approximate fused C, preserving the same contract. Require a measured incremental gain beyond fusion itself. Validate worst-case errors over dense probes and adversarial boundary cases; no continuous-domain proof from sampling alone. Fall back or reject outside the validated domain. Preserve an exact path.

### Predeclared go/no-go gates (proposed, not yet achieved)

- At least **20% end-to-end latency reduction** or **25% throughput improvement** versus the strongest relevant baseline at a representative batch size, on stable hardware across >= 30 paired runs, with no p95 regression.
- Absolute and relative error tolerances set **before** tuning, including near-zero behavior; no silent fallback, no nonfinite outputs, no data corruption.
- Positive net benefit after conversion, compilation amortization and maintenance; one realistic adopter or deployment path.
- If these fail: stop performance-product development and preserve the toolkit as research infrastructure.

## Concrete next work

1. Add a benchmark harness for a real repeated vector workload, with exact fused C and vectorized baseline, no approximate math initially.
2. Make benchmark outputs machine-readable, including environment, build hash, error metrics, and conversion breakdown.
3. Compare with a strong optimized baseline before implementing an approximation or WASM.
4. Validate user demand: identify an actual CPU-bound pipeline, measured bottleneck and willingness to adopt.
5. Keep existing SDK as correctness/control harness; do not auto-select experimental backends.

## Evidence and limitations

- [Matched pilot SDK measurements](PILOT-CPU-BENCHMARK-2026-11-19.md)
- [Earlier experiment and integration report](INTEGRATION-AND-EXPERIMENT-2026-11-19.md)
- [GitHub CI](https://github.com/bahira/spear-unified/actions/runs/44602944355)
- No production customer measurements, real deployment, or positive acceleration result currently documented.
