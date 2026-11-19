# Goal: SPEAR — workload-specific CPU optimization with measurable asymmetric edge

**North star:** lower end-to-end cost of a real repeated CPU-bound workload, under explicit accuracy, reliability and integration constraints. A formula-discovery tool is supporting infrastructure, not the product.

## Current evidence (2026-11-19)
- Working Python SiLU/GELU ledger, bounded symbolic discovery, checksum provenance, CPU pilot SDK and automated tests.
- Matched-contract Python ledger is **slower** than direct reference (1.40–2.58× duration on six CI scenarios); no production speedup.
- An **opt-in**, separately bounded SpearVM PackedNT+GELU native adapter has now been built and executed in GitHub Actions on an AVX2/FMA Linux runner (PR #41). On **synthetic** f32 weights (128,64), batch 1024 measured 1.524 ms packed vs 3.326 ms unpacked (2.18×) and 3.712 ms NumPy+native GELU; smaller batches were not consistently faster. Single shared-runner evidence, strong PyTorch/ORT baseline and application workload still missing. No native production backend or WASM gain is established.
- Complete research-site manuscripts were reviewed and a pendulum-control stability-claim error reproduced (PR #38); independent quality audits for float32 approximation and composition were added (PR #39). These safeguards do not prove hardware precision or safety.
- [First-principles strategic review](reports/FIRST-PRINCIPLES-EDGE-2026-11-19.md) defines the economic model, hypotheses and kill criteria.

## Ordered priorities
1. Find a repeated real CPU bottleneck with an adopter and measurable costs; capture representative input shapes and quality requirements.
2. Reproduce the opt-in SpearVM result on a **real small MLP workload**, with the strongest optimized CPU baselines (PyTorch/ONNX Runtime and BLAS), full conversion/serialization costs, 30+ paired repeats and stable dedicated hardware. Keep preparation/weight amortization separate.
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
