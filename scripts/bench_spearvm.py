"""Opt-in exact-contract CPU benchmark of SpearVM packed vs unpacked f32 GELU.

Run only when spur-math is explicitly installed:
  python -m scripts.bench_spearvm
  python -m scripts.bench_spearvm --smoke
No production backend selection or measured performance claim until reports.
"""
import argparse
import hashlib
import importlib.metadata
import json
import math
import platform
import statistics
import time

from spear.spearvm import SpearVMPackedGELU, cpu_supported


def _median(values):
    return statistics.median(values)


def _p95(values):
    values = sorted(values)
    return values[max(0, math.ceil(.95 * len(values)) - 1)]


def benchmark(size, adapter, weights, bias, np, sm, *, repeats=31):
    rng = np.random.default_rng(712 + size)
    x = rng.normal(0, 0.75, size * weights.shape[1]).astype(np.float32)
    x = x.reshape(size, weights.shape[1])
    variants = {
        'packed': lambda: adapter.compute(x)['values'],
        'unpacked_native': lambda: sm.matmul_nt_gelu(x, weights, bias),
        'numpy_then_native_gelu': lambda: sm.gelu_erf(x @ weights.T + bias).astype(np.float32),
    }
    independent = (x.astype(np.float64) @ weights.astype(np.float64).T) + bias.astype(np.float64)
    expected = np.fromiter((.5*t*(1+math.erf(t/math.sqrt(2)))
                            for t in independent.flat), dtype=np.float64,
                           count=independent.size).reshape(independent.shape)
    errors = {}
    for label, run in variants.items():
        actual = run()
        error = float(np.max(np.abs(actual.astype(np.float64)-expected)))
        if actual.shape != expected.shape or not np.isfinite(actual).all() or error > .001:
            raise ValueError(f'Accuracy budget failed: {label} {error}')
        errors[label] = error
    for run in variants.values():
        for _ in range(3):
            run()
    names = list(variants)
    raw = {name: [] for name in names}
    sink = 0.0
    for rep in range(repeats):
        order = names[rep % len(names):] + names[:rep % len(names)]
        if rep % 2:
            order.reverse()
        for label in order:
            start = time.perf_counter_ns()
            arr = variants[label]()
            raw[label].append(time.perf_counter_ns() - start)
            sink += float(arr[0, 0])
    median = {k: _median(v) for k, v in raw.items()}
    p95 = {k: _p95(v) for k, v in raw.items()}
    return {'batch': size, 'median_ns': median, 'p95_ns': p95,
            'max_abs_error': errors,
            'packed_vs_unpacked_time_ratio': median['packed'] / median['unpacked_native'],
            'packed_vs_numpy_time_ratio': median['packed'] / median['numpy_then_native_gelu'],
            'raw_ns': raw, 'sink': sink}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    if not cpu_supported():
        print(json.dumps({'status': 'unsupported', 'reason': 'AVX2/FMA Linux host required'}))
        return 0
    try:
        import numpy as np
        import spur_math as sm
    except ImportError as exc:
        print(json.dumps({'status': 'unavailable', 'reason': str(exc)}))
        return 3
    rng = np.random.default_rng(911)
    weights = (rng.standard_normal((128, 64)) * 0.025).astype(np.float32)
    bias = (rng.standard_normal(128) * 0.01).astype(np.float32)
    begin = time.perf_counter()
    adapter = SpearVMPackedGELU(weights, bias)
    pack_ms = (time.perf_counter() - begin) * 1000
    sizes = (1, 32) if args.smoke else (1, 32, 256, 1024)
    results = [benchmark(n, adapter, weights, bias, np, sm,
                         repeats=5 if args.smoke else 31) for n in sizes]
    try:
        version = importlib.metadata.version('spur-math')
    except importlib.metadata.PackageNotFoundError:
        version = 'unversioned'
    report = {'status': 'ok', 'backend': 'optional-SpearVM-0.5.3',
              'spur_math_version': version,
              'machine': platform.platform(), 'python': platform.python_version(),
              'weight_sha256': hashlib.sha256(weights.tobytes()).hexdigest(),
              'weights_shape': list(weights.shape), 'packed_setup_ms': pack_ms,
              'repeats': 5 if args.smoke else 31, 'warmups': 3, 'results': results,
              'included': 'NumPy f32 contiguous inputs, native fused calls, output ndarray; full adapter validation and returned dict for packed variant',
              'excluded': 'Initial import/compilation, input construction, JSON/network serialization and any downstream app',
              'caveat': 'Synthetic weights and inputs, CI runner noise. NumPy baseline uses native f64 GELU then converts to f32; accuracy checked independently. No production win or general speedup claim.'}
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
