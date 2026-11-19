# SpearVM packed CPU integration — first native CI result (2026-11-19)

Status: **experimental, not production promoted**.

Source backend: [bahira/SpearVM](https://github.com/bahira/SpearVM) pinned at `113d2e2506e8d50cbb67bcd5563e56968fa0e37c`, `spur-math 0.5.3`. CI run: [44611395366](https://github.com/bahira/spear-unified/actions/runs/44611395366), optional Linux x86_64 AVX2/FMA CPU job, Python 3.12. The standard Unified validation run [44611395347](https://github.com/bahira/spear-unified/actions/runs/44611395347) also passed three jobs.

## Real deployment issue found and resolved for experiment

A first attempt `pip install spur-math==0.5.3` succeeded but Linux `import spur_math` failed: native binary absent and runtime could not find/compile native sources in the installed wheel. We did **not** hide this failure. The experiment workflow now checks out a pinned native source revision, runs SpearVM's `build_package.py --install`, then executes its actual native C kernels. This is a *workflow workaround*, not a repaired PyPI wheel for general users.

## Experiment and measurements

Synthetic deterministic float32 weights shaped (128,64), same bias and inputs across all paths. Outputs: float32 NumPy arrays. Three paths:
- `packed`: `SpearVMPackedGELU.compute` wrapping `PackedNT.matmul_gelu`, with input/output safety checks and dict.
- `unpacked_native`: `spur_math.matmul_nt_gelu`.
- `numpy_then_native_gelu`: NumPy BLAS matrix multiply then native `gelu_erf` on f64 and conversion to f32.

Each operation was warmed up, and timings are medians from **31 alternating-order repetitions** on a shared GitHub runner. Table shows milliseconds per batch, **lower is better**.

| Batch | Packed ms | Unpacked C ms | NumPy+GELU ms | Packed / unpacked duration |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 0.0410 | 0.0301 | 0.0316 | 1.36× (slower) |
| 32 | 0.0798 | 0.0664 | 0.0511 | 1.20× (slower) |
| 256 | 0.4815 | 0.3963 | 4.0255 | 1.22× (slower) |
| 1024 | **1.5241** | 3.3256 | 3.7117 | **0.458× (2.18× faster)** |

At 1024: packed measured **2.18×** faster than unpacked and **2.44×** faster than the NumPy+native GELU path on this *specific* shared runner and shape. At batches <=256, packed was slower than unpacked C. p95 timings were noisy, including a 2.09 ms packed outlier at batch 32; this is **not** stable proof of any general throughput advantage.

Numerical accuracy: max abs deviation from independent double-precision `math.erf` GELU reference was <= **6.01e-6** for these inputs. Prepack setup after module import: **0.337 ms**. Compilation/import time excluded. Note that NumPy+GELU first uses f64 activation, so although returned array and independent accuracy budget match, implementations do not have strictly identical intermediate precision.

## Contract / safety

- `SpearVMPackedGELU` is a separate **explicit opt-in** backend, not a silent alternative for scalar `CPUPilot`.
- Runtime module import is lazy; constructor rejects unsupported Linux/x86 AVX2/FMA hosts before native import. No fallback.
- Finite fixed float32 weights/bias and 2D inputs, bounded allocations, immutable weight copies and output finite/shape checks.
- Optional independent libm output quality check with explicit max-absolute-error budget, also fail closed.
- No proof of general interval precision, native C/WASM parity or production latency.

## Decision

Keep behind explicit opt-in only. This **is the first direct positive measured hint** in Unified's new strategy for a *particular batch size*, but it does **not** yet satisfy GOAL's commercial gate against the strongest relevant optimized baseline with stable hardware and realistic application workload. Re-test with PyTorch CPU/ONNX Runtime, 64→128→10 digits model serving (real data), conversion/serialization and larger independent run sets on dedicated hardware.

## Commands

```sh
python -m unittest tests.test_spearvm_adapter -v
python -m scripts.bench_spearvm
```

Run with the pinned source build as in `.github/workflows/spearvm-experiment.yml`; PyPI 0.5.3 Linux installation alone currently failed on CI.
