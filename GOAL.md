# Goal: SPEAR — workload-specific CPU optimization with measurable asymmetric edge

**North star:** lower end-to-end cost of a real repeated CPU-bound workload, under explicit accuracy, reliability and integration constraints. A formula-discovery tool is supporting infrastructure, not the product.

## Current evidence (2026-11-19)
- Working Python SiLU/GELU ledger, bounded symbolic discovery, checksum provenance, CPU pilot SDK and automated tests.
- Matched-contract Python ledger is **slower** than direct reference (1.40–2.58× duration on six CI scenarios); no production speedup.
- Native C probes exist but are **not** a production backend. No customer workload, matched native/vectorized benchmark, or WASM result yet.
- [First-principles strategic review](reports/FIRST-PRINCIPLES-EDGE-2026-11-19.md) defines the economic model, hypotheses and kill criteria.

## Ordered priorities
1. Find a repeated real CPU bottleneck with an adopter and measurable costs; capture representative input shapes and quality requirements.
2. Benchmark the strongest existing optimized baseline, exact fused native implementation and full conversion/serialization overhead.
3. Only after positive fusion evidence, experiment with bounded-domain approximation and independent accuracy checks.
4. Apply predeclared go/no-go gates: >=20% end-to-end latency reduction **or** >=25% throughput improvement, >=30 paired runs on stable hardware, no p95 regression, precision and fallback safety, positive amortized economics.
5. Consider WASM only for a concrete browser/edge deployment need; browser/LLM adapters are out of scope until then.

## Non-goals
- Generic acceleration claims, automatic backend promotion, adding unsupported backends for feature count, or optimizing Python scalar approximations without a workload.
- Treating synthetic CI timing as proof of real customer savings.

## Existing engineering constraints
Preserve reproducibility, deterministic provenance, strict finite domains, bounded execution, independent baselines and lightweight testing. Keep experimental backends opt-in. Source instructions: AGENTS.md and .agents/skills/triple-helix/SKILL.md.

## Completion criteria
One documented, independently reproducible, accuracy-safe, economically meaningful win against the strongest relevant baseline on an actual workload — **or** an explicit no-go decision backed by data.
