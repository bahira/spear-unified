# First fused-kernel experiment — 2026-11-19

Source: [GitHub Actions run 44603895835](https://github.com/bahira/spear-unified/actions/runs/44603895835), Python 3.12 Linux x86_64, C compiler `-O3 -fno-fast-math -ffp-contract=off`, NumPy installed, 31 alternating-order repetitions, 3 warmups. Exact synthetic pipeline `z=clip(0.75*x+0.125,0,6); y=z*z+0.25*x`, full Python list input and output. Precision checked against Python reference to 1e-12.

| Batch | Python scalar ms | C fused + list conversion ms | NumPy vectorized + list output ms | C / NumPy speed ratio |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 0.001152 | 0.004972 | 0.010762 | 2.16× |
| 64 | 0.039873 | 0.008332 | 0.015387 | 1.85× |
| 4096 | 1.347351 | 0.185471 | 0.183136 | 0.987× |
| 65536 | 21.988967 | 3.104776 | 3.105545 | 1.000× |

C fused **does beat the scalar Python baseline** for batches >=64, but **does not beat NumPy materially at 4096/65536**. The small-batch NumPy differences reflect per-call overhead; they are not a proven sustainable advantage. At batch 1, C is slower than Python scalar. This is a synthetic workload, not a customer case, and CI timing is noisy. No approximation is used. There is **no evidence yet of the >=20% end-to-end win on a real workload** required by GOAL.md.

**Decision:** do not promote C as a general backend. Investigate conversion overhead and select a real workload with measured bottlenecks before additional optimization. If NumPy or an existing compiler already solves it, stop.

Code: `scripts/bench_fused_pipeline.py`; tests: `tests/test_fused_pipeline.py`.
