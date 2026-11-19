# SPEAR research + integration session — verified progress (2026-11-19)

**Result:** four SPEAR Unified PRs (#38–#41) and one SpearVM PR (#4) merged after passing CI. No production speedup claim or unrequested backend promotion.

## Shipped and independently observable

| Repository / PR | Shipped work | Evidence |
|---|---|---|
| [Unified #38](https://github.com/bahira/spear-unified/pull/38) | Recovered complete nine research-site papers, critical source review, executable embedded-controller mathematical counterexample, four regression tests | [CI](https://github.com/bahira/spear-unified/actions/runs/44607714950), 3 jobs green |
| [Unified #39](https://github.com/bahira/spear-unified/pull/39) | Pinned-ledger f32 step-rounded and f64 error audits, bounded-domain and inverse-composition gate, fail-closed CLI, nine unit tests | [CI](https://github.com/bahira/spear-unified/actions/runs/44608913366), 3 jobs green |
| [Unified #40](https://github.com/bahira/spear-unified/pull/40) | Proven positive local eigenvalue for the printed pendulum and corrected 84 MHz clock arithmetic, two tests, proposed erratum, 20-point progress checkpoint | [CI](https://github.com/bahira/spear-unified/actions/runs/44610044745), 3 jobs green |
| [Unified #41](https://github.com/bahira/spear-unified/pull/41) | Optional native SpearVM PackedNT fused-GELU adapter, real integration tests and benchmark against unpacked/native+NumPy, source pinned | [Native CI](https://github.com/bahira/spear-unified/actions/runs/44611395366) and [final CI](https://github.com/bahira/spear-unified/actions/runs/44611826778), passing |
| [SpearVM #4](https://github.com/bahira/SpearVM/pull/4) | Linux source packaging repair, clean sdist install/import and wheel-content CI checks | [CI](https://github.com/bahira/SpearVM/actions/runs/44612340836), 4 jobs green |

## Key empirical outcomes

- **Numerical falsification:** the published inverted pendulum `Vdot` misses the `(5/2)mglωsinθ` term; sample `Vdot_actual=+0.0711796` versus paper `Vdot_claimed=-0.0012967`. A local linearized eigenvalue is **+1.0091/s**. Published `3 cycles at 84 MHz=4.2 ns` is inconsistent: arithmetic yields **35.71 ns** even if 3 cycles were correct.
- **Accuracy:** bounded step-rounded f32 SiLU reference check 257 points gave max absolute error **5.81e-7** in one GitHub Actions run (illustrative 1.0 tolerance); not C native parity.
- **Native:** one synthetic batch-1024 test measured packed SpearVM **1.524 ms** against **3.326 ms** for un-packed C (2.18×) and **3.712 ms** for NumPy+GELU (2.44×), with max abs error **6.01e-6**. Packed was slower than C at batches 1/32/256. Shared VM timing was noisy; no strong PyTorch/ORT comparison yet.
- **Packaging:** published PyPI spur-math 0.5.3 Linux installation failed to import in first CI; pinned source build worked. Native source packaging fixed in SpearVM repository and CI, but a **new PyPI publication is still required** for downstream consumers.

## Persistent blockers (not completed)

1. A real CPU-bound adopter/workload with model-quality target, payload shapes, and cost economics.
2. Matched PyTorch CPU / ONNX Runtime baseline on actual digits MLP or another representative deployed workload; fixed hardware p50/p95 with 30+ runs and packing amortization.
3. Native f32 semantics and C/WASM parity across compiler flags; no promotion before validated budgets.
4. Public-site paper erratum not published: the GitHub connector returned HTTP 403 trying to create a branch in `rabdelaal/rabdelaal.github.io`. Proposed correction in `reports/RESEARCH-SITE-ERRATUM-PROPOSAL-2026-11-19.md`.
5. Next spur-math PyPI release/reproducible clean install from published artifact, not just merged source.

## Tracking

- [Unified paper source/reproduction issue #37](https://github.com/bahira/spear-unified/issues/37), remaining benchmark work.
- [Unified numerical gates issue #34](https://github.com/bahira/spear-unified/issues/34), hardware-native precision parity outstanding.
- [Unified performance baseline issue #32](https://github.com/bahira/spear-unified/issues/32), real workload strong baseline outstanding.
- [SpearVM packaging issue #3](https://github.com/bahira/SpearVM/issues/3), new PyPI release pending.

**Scope of visualization:** only numerical plots generated from local RK4 and CI measurements; no site UI or graphics game screenshots were produced because no visual product was changed.
