# SPEAR Unified — CPU pilot benchmark, 2026-11-19

## Delivered
PR #26 integrated advanced sample-based symbolic regression and baselines. PR #27 delivered `spear.pilot.CPUPilot`, an explicit, bounded reference/ledger SDK with numeric domain checks, per-value error measurement, optional fail-closed tolerance, tests and a matched-contract benchmark. No C or WASM backend is active.

## Actual measurement
[GitHub Actions run 44602944355](https://github.com/bahira/spear-unified/actions/runs/44602944355), Python 3.12 on shared Linux Azure runner. Seven alternating-order repeats, warmed up, sizes 1/64/4096. Full SDK contract includes validation, output, and error measurement. Values below are median milliseconds **per batch**.

| Kernel | Batch | Reference ms | Python ledger ms | Ledger / reference time |
| --- | ---: | ---: | ---: | ---: |
| SiLU | 1 | 0.002485 | 0.003857 | 1.552 |
| SiLU | 64 | 0.039273 | 0.097983 | 2.495 |
| SiLU | 4096 | 4.909303 | 12.670388 | 2.581 |
| GELU | 1 | 0.004198 | 0.005882 | 1.401 |
| GELU | 64 | 0.088585 | 0.166290 | 1.877 |
| GELU | 4096 | 2.490038 | 6.393443 | 2.568 |

**Interpretation:** the ledger backend is slower on all six measured cases. This does not prove an optimization and does not benchmark the experimental C native path or WASM. CPU runner scheduling, small sample counts and the cost of numerical checking can affect results. The result is a concrete negative result, not a speedup claim.

## Next technical acceptance gates
1. Implement an opt-in native backend with the **same API and validation contract**, using a clearly specified target kernel and mathematically independent reference.
2. Compare Python reference, ledger and C native over identical inputs, including list/buffer conversion and output serialization, with precision budgets and fallback policy.
3. Repeat on stable dedicated hardware and real workload distributions; only promote a backend if statistically meaningful end-to-end gain and numerical safety both hold.
4. Consider WASM only if browser deployment is a concrete requirement. Do not infer WASM performance from native C.

## Commands
```sh
python -m unittest discover -s tests -v
python -m scripts.bench_pilot
python -m scripts.bench_end_to_end --samples 257 --repeats 3 --warmups 1
```

The SDK and report are experimental and do not provide a network service or claim production readiness.
