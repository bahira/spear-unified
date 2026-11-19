# Nine research-site papers — evidence triage (2026-11-19)

Source: https://rabdelaal.github.io/#papers. All nine links were opened. **Critical limitation:** paper pages return only metadata and “Loading paper content...” to the available web fetcher. The paper bodies, methods, proofs, benchmark scripts, and empirical results were **not independently reviewed**. Accordingly this report is an evidence-gated *triage*, not a paper validation or implementation.

| Paper | Site metadata/abstract topic | Potential Unified reuse | Evidence status | Gate |
|---|---|---|---|---|
| SSR Architecture | Three-kernel system architecture | Modular separation of discovery, verification, execution | Abstract only | Obtain complete manuscript and executable specification |
| SSR Omega | Modular parallel interpretable reasoning | Optional orchestration patterns | Abstract only | Benchmark against simple scheduler |
| vTRN | Claimed O(n) sequence processing | Streaming sequence workload candidate | Abstract only | Check full algorithm, quality and optimized attention baselines |
| is-vTRN | Temporal sparsity/inertial speculation | Sparse time-series CPU specialization | Abstract only | Verify sparsity benefit and worst-case fallback |
| SDRC | Speculative decomposition with residue correction | Speculative fast path + independently checked residual/fallback | Abstract only | Prove correction bound and full pipeline benefit |
| SyS-Fused | Fused synaptic speculation/latency hiding | Fusion + reuse with SpearVM/TensorFold kernels | Abstract only | Same-workload p50/p95, quality and setup amortization |
| GEPARD | Genetic policy and representation | Search over constrained control policies | Abstract only | Held-out control tasks, safety envelope, timing |
| Cognitive Resonance Cascade | Layered reasoning cascade | Low relevance to numerical CPU bottleneck | Abstract only | Defer unless real application |
| SPEAR embedded control | Symbolic policy evolution, robust embedded control | Bounded domain + certifiable fast controller | Abstract only | Obtain manuscript, numerical error and WCET proof on hardware |

## Decision

Do **not** copy formulas, claim verification, or add dependencies on the basis of titles/abstracts. First request/download actual Markdown/manuscript source and associated tests. Prioritize **SyS-Fused, SDRC, embedded SPEAR** for a falsifiable prototype. They could supply the *selection, correction and safety* layer around the existing specialized kernels.

## Proposed integration design

`WorkloadContract` (shape/dtype/domain/precision) → `CandidateBackend` (native fused, packed, reference) → `QualityGate` (independent reference + residual/boundary probes) → `MeasuredDecision` (paired p50/p95, amortized cost) → explicit opt-in backend. No automatic speculative promotion.

A correction scheme is useful only when its residual is cheaper than full exact computation, error bounds are valid, and fallback overhead is accounted for. For approximate controllers, validate worst-case latency and domain invariant, not only average speed.

## Next steps

1. Retrieve complete Markdown source for all nine pages (site dynamically loads them).
2. Match each paper's algorithm to an accessible GitHub repository and tests.
3. Verify claims against reproducible datasets and optimized baselines.
4. Prototype one narrow workload with error-controlled speculation and fusion.
5. Reject if matched full-pipeline latency fails the GOAL >=20% improvement or >=25% throughput, or if quality/p95 regresses.

No new benchmark, screenshot of a running model, or numerical reproduction was performed for these nine papers.
