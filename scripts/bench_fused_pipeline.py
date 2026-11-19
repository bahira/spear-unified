"""Bounded first-principles fusion experiment: exact C vs Python and optional NumPy.

No automatic backend selection. Measures full list->buffer->list conversion.
Pipeline: y = max(0, min(6, 0.75*x+0.125)) ** 2 + 0.25*x
This is an illustrative workload, NOT a measured customer bottleneck.
"""
from array import array
import ctypes
import hashlib
import json
import math
import platform
from pathlib import Path
import shutil
import statistics
import subprocess
import tempfile
import time

C_SOURCE = r"""
#include <stddef.h>
void fused(const double *xs, double *ys, size_t n) {
  for(size_t i=0;i<n;i++) {
    double x=xs[i], z=0.75*x+0.125;
    if(z<0.0) z=0.0;
    if(z>6.0) z=6.0;
    ys[i]=z*z+0.25*x;
  }
}
"""
FLAGS = ['-O3', '-std=c11', '-fPIC', '-shared', '-fno-fast-math', '-ffp-contract=off']


def scalar(x):
    z = min(6.0, max(0.0, 0.75*x + 0.125))
    return z*z + 0.25*x


def python_baseline(xs):
    return [scalar(x) for x in xs]


def compile_native(directory):
    compiler = shutil.which('cc')
    if not compiler or platform.system() != 'Linux':
        raise RuntimeError('Native experiment requires Linux and cc')
    source = Path(directory) / 'fused.c'
    library = Path(directory) / 'fused.so'
    source.write_text(C_SOURCE)
    subprocess.run([compiler, *FLAGS, str(source), '-o', str(library)],
                   check=True, capture_output=True, text=True, timeout=10)
    lib = ctypes.CDLL(str(library))
    fn = lib.fused
    fn.argtypes = [ctypes.POINTER(ctypes.c_double),
                   ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
    fn.restype = None
    return fn


def native_list(xs, fn):
    incoming = array('d', xs)
    outgoing = array('d', [0.0]) * len(incoming)
    view = ctypes.c_double * len(incoming)
    fn(view.from_buffer(incoming), view.from_buffer(outgoing), len(incoming))
    return list(outgoing)


def optional_numpy(xs):
    import numpy as np
    a = np.asarray(xs, dtype=np.float64)
    z = np.clip(0.75*a + 0.125, 0, 6)
    return (z*z + 0.25*a).tolist()


def benchmark(size, fn, repeats=31):
    xs = [-8.0 + 16.0*i/max(1, size-1) for i in range(size)]
    variants = {'python': lambda: python_baseline(xs),
                'c_fused_list': lambda: native_list(xs, fn)}
    try:
        import numpy
        variants['numpy_vectorized'] = lambda: optional_numpy(xs)
    except ImportError:
        pass
    expected = variants['python']()
    for name, run in variants.items():
        actual = run()
        error = max((abs(a-b) for a, b in zip(actual, expected)), default=0.0)
        if len(actual) != len(expected) or not math.isfinite(error) or error > 1e-12:
            raise ValueError(f'Precision check failed: {name} error={error}')
    for run in variants.values():
        for _ in range(3):
            run()
    raw = {name: [] for name in variants}
    names = list(variants)
    sink = 0.0
    for rep in range(repeats):
        order = names[rep % len(names):] + names[:rep % len(names)]
        if rep % 2:
            order.reverse()
        for name in order:
            start = time.perf_counter_ns()
            result = variants[name]()
            raw[name].append(time.perf_counter_ns() - start)
            sink += result[-1] if result else 0
    median = {name: statistics.median(times) for name, times in raw.items()}
    return {'size': size, 'median_ns_per_batch': median,
            'c_vs_python_speedup': median['python']/median['c_fused_list'],
            'c_vs_numpy_speedup': median.get('numpy_vectorized', float('nan'))/median['c_fused_list']
            if 'numpy_vectorized' in median else None,
            'raw_ns_per_batch': raw, 'sink': sink}


def main():
    with tempfile.TemporaryDirectory(prefix='spear-fusion-') as directory:
        t = time.perf_counter()
        fn = compile_native(directory)
        build_ms = (time.perf_counter()-t)*1000
        results = [benchmark(size, fn) for size in (1, 64, 4096, 65536)]
    report = {'status': 'ok', 'experiment': 'exact_fused_pipeline',
              'platform': platform.platform(), 'python': platform.python_version(),
              'compiler': shutil.which('cc'), 'compiler_flags': FLAGS,
              'source_sha256': hashlib.sha256(C_SOURCE.encode()).hexdigest(),
              'build_ms': build_ms, 'repeats': 31, 'warmups': 3,
              'results': results,
              'included': 'Python input list, list-to-native conversion, allocation, C compute, native-to-list output; NumPy baseline also converts output to list',
              'excluded': 'Input generation, compile/cold load (build_ms separate), network, deployment, JSON',
              'limitations': 'Synthetic illustrative pipeline, shared CI VM, NumPy optional; not a real customer workload or proof of an asymmetric edge.'}
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
