# SpearVM → SPEAR Unified: first-principles reuse audit (2026-11-19)

Upstream: https://github.com/bahira/SpearVM (branch `master`, MIT, `spur-math` 0.5.3). Review based on source files and upstream benchmark reports; **no new independent SpearVM runtime benchmarking in this audit**.

## Executive decision

**Integrate by optional dependency/adapter, not wholesale code copying.** The highest-probability candidate for defensible value is *repeated inference of small CPU MLPs with fixed/prepacked weights*, not general transcendental scalar acceleration or broad Transformer inference.

SPEAR Unified already benchmarks SiLU/GELU against direct math and has a proof-of-concept fused C pipeline; existing CI shows no material advantage over NumPy on large arrays. SpearVM's `PackedNT` / `PackedMLP` and graph fusion therefore provide a more valuable candidate execution engine.

## Reuse priority and engineering constraints

| Priority | Upstream code | Why useful | Gate |
| --- | --- | --- | --- |
| P0 | `spur_math.nn.PackedMLP`, `spur_math.PackedNT`, `matmul_nt_gelu` in `src/spur_kernels.c` | Prepack immutable weights once; fuse GEMM+bias+GELU and reuse in small batched inference | Compare on matched fixed weights/shapes and p50/p95 with strong NumPy/PyTorch CPU/ORT baselines, include preparation amortization |
| P0 | `docs/USECASES.md`, `examples/usecases/digits_batch_serving.py` | Existing test candidate and observed high-throughput regime | Reproduce results on representative hardware, version pinning and optimized baselines |
| P1 | `spur_math/graph.py` | Explicit use-count check before fusing matmul→GELU; avoids dropping output needed by consumers | Add graph equivalence tests for multiple consumers, training backward, shapes and error tolerance |
| P1 | runtime ISA dispatch and AVX2/AVX-512 CPU kernels in `src/spur_kernels.c`, `spur_math/__init__.py` | Architecture-aware execution already written | Must not load on non-AVX2 hosts, support explicit unsupported status; avoid dynamic compilation in default installs |
| P2 | `src/spur_posix.c` mini-JIT | Potential specialization of repeated graphs | Security/ABI/W^X/caching scrutiny; no advantage measured yet; defer |
| P2 | `spur_math.nn.SpearMLP`, `Adam` | Training of small networks | Secondary product to serving; gradient and numerical regression gate |
| Do not transplant | legacy GELU v1/quintic or approximate math by default | Errors materially exceed reference; weak relevance to accuracy-sensitive users | Optional only with predeclared error budget |

## Actual upstream reported evidence (not reproduced here)

From `docs/USECASES.md`: digits MLP training 0.41s vs 0.71s PyTorch (same stated accuracy); digits serving batches 32: ~1.080M vs ~0.542M samples/sec and batch 1024: ~2.820M vs ~2.279M; batch 1 numpy is slightly faster; a simple logistic regression wins on the tabular breast cancer benchmark. Dataset sizes are small and shared 2-core CI/VM performance is environment-specific.

From README and `docs/BENCH_ENCODER_E2E.md`: GEMM-only is ~1.3–1.6× slower than OpenBLAS, and a 12-layer Transformer encoder hybrid is slower than PyTorch/ONNX Runtime. Treat the asymmetry as workload-specific.

**Important precision qualification:** `gelu_erf` is labeled “exact” in upstream API, but the implementation is still a rational approximation; upstream itself reports max absolute error ~2.05e-5 versus the mathematical GELU. Use error budgets, not the literal “exact” label, to make deployment decisions.

## Integration design

1. SPEAR Unified's Python `CPUPilot` remains deterministic correctness oracle / input-domain gate, not the speed path.
2. Create a separate `SpearVMBackend` adapter that lazily imports `spur_math`, checks supported CPU + platform, handles contiguous float32 inputs and fixed immutable prepacked weights. **Never import or build SpearVM on normal SPEAR Unified module import.**
3. Expose a distinct, opt-in `inference_mlp` capability; do not misrepresent it as an alternative backend for SiLU/GELU scalar `CPUPilot.compute`.
4. Benchmark *the full inference pipeline* at batch 1, 8, 32, 256, 1024, including input conversion, weight packing separately, steady-state calls, output transfer and memory usage.
5. Validate output discrepancy against a strong independently implemented reference on held-out inputs; add drift and shape tests, CPU capability check, and fallback that is always visible.
6. Only then decide whether the optional backend merits production packaging. Do not copy the entire C runtime into SPEAR Unified.

## Predeclared go/no-go conditions

- **Required:** same weights and model, same input/output contract and numeric budget; p50/p95 recorded across >=30 paired runs on stable hardware.
- **Proposed commercial gate:** >=20% lower end-to-end latency OR >=25% throughput improvement versus the *strongest* relevant optimized CPU reference, with no meaningful regression at the targeted batch sizes.
- Show payback of packing/setup costs over realistic model reuse count.
- If not achieved, keep the adapter as an experiment and do not market a general acceleration claim.

## Repository source links

- https://github.com/bahira/SpearVM/blob/master/spur_math/nn.py
- https://github.com/bahira/SpearVM/blob/master/spur_math/graph.py
- https://github.com/bahira/SpearVM/blob/master/src/spur_kernels.c
- https://github.com/bahira/SpearVM/blob/master/tests/test_packed.py
- https://github.com/bahira/SpearVM/blob/master/docs/USECASES.md
- https://github.com/bahira/SpearVM/blob/master/docs/BENCH_ENCODER_E2E.md

## Next executable experiment

Build a no-network, opt-in benchmark `scripts/bench_spearvm_adapter.py`, separate optional `spur_math` installation, and CI that **skips cleanly** on unsupported CPU/OS. Validate a fixed 64→128→10 MLP on identical f32 weights and repeatable inputs, with NumPy and PyTorch/ONNX when installed. Report prepack initialization and steady-state latencies separately. No dependency added to SPEAR Unified base installation.
