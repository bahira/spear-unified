"""Opt-in experimental SpearVM packed GEMM+bias+GELU adapter.

Separate from CPUPilot scalar kernels. Does not load/compile spur_math at
import time; explicit construction may invoke spur_math's native build.
Linux x86_64 AVX2/FMA only, fail closed on unsupported platforms.
Not production-promoted and no performance claims.
"""
import importlib
import math
import platform
from pathlib import Path

MAX_ELEMENTS = 262144


def cpu_supported():
    """Conservative Linux CPU guard before importing code compiled for AVX2/FMA."""
    if platform.system() != 'Linux' or platform.machine().lower() not in ('x86_64', 'amd64'):
        return False
    try:
        flags_lines = [line for line in Path('/proc/cpuinfo').read_text().splitlines()
                       if line.startswith('flags') and ':' in line]
        if not flags_lines:
            return False
        return all({'avx2', 'fma'} <= set(line.split(':', 1)[1].split())
                   for line in flags_lines)
    except (OSError, UnicodeError):
        return False


class SpearVMPackedGELU:
    """Fixed immutable f32 weights, pre-packed once, explicit experimental call."""

    backend = 'spearvm-packed-gelu'
    runtime_promoted = False

    def __init__(self, weights, bias, *, max_elements=MAX_ELEMENTS):
        if type(max_elements) is not int or not 1 <= max_elements <= MAX_ELEMENTS:
            raise ValueError('Invalid max_elements')
        if not cpu_supported():
            raise RuntimeError('SpearVM requires Linux x86_64 AVX2+FMA; no fallback')
        try:
            np = importlib.import_module('numpy')
            sm = importlib.import_module('spur_math')
        except ImportError as exc:
            raise RuntimeError('Optional numpy/spur_math runtime unavailable; no fallback') from exc
        try:
            w = np.array(weights, dtype=np.float32, copy=True, order='C')
            b = np.array(bias, dtype=np.float32, copy=True, order='C')
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError('Invalid float32 weights/bias') from exc
        if w.ndim != 2 or b.ndim != 1 or min(w.shape) < 1 or b.shape != (w.shape[0],):
            raise ValueError('Expected weights (out,in) and bias (out,)')
        if w.size > max_elements or not np.isfinite(w).all() or not np.isfinite(b).all():
            raise ValueError('Weight bounds or finite check failed')
        w.setflags(write=False)
        b.setflags(write=False)
        self._np, self._sm = np, sm
        self.weights, self.bias = w, b
        self.max_elements = max_elements
        self._packed = sm.PackedNT(w)

    def compute(self, x, *, max_abs_error=None):
        """Return NumPy f32 output; optional full independent libm error check."""
        np = self._np
        try:
            a = np.asarray(x, dtype=np.float32)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError('Invalid input') from exc
        if (a.ndim != 2 or a.shape[0] < 1 or a.shape[1] != self.weights.shape[1] or
                a.size > self.max_elements or a.shape[0] * self.weights.shape[0] > self.max_elements or
                not np.isfinite(a).all()):
            raise ValueError('Input dimensions, finite values or size limit violated')
        if max_abs_error is not None and (type(max_abs_error) not in (int, float) or
                                           not math.isfinite(max_abs_error) or max_abs_error < 0):
            raise ValueError('Invalid precision budget')
        a = np.ascontiguousarray(a, dtype=np.float32)
        out = self._packed.matmul_gelu(a, self.bias)
        if out.shape != (a.shape[0], self.weights.shape[0]) or not np.isfinite(out).all():
            raise ValueError('Non-finite or malformed native output')
        error = None
        if max_abs_error is not None:
            z = a.astype(np.float64) @ self.weights.astype(np.float64).T
            z += self.bias.astype(np.float64)
            expected = np.fromiter((0.5 * t * (1 + math.erf(t / math.sqrt(2.0)))
                                    for t in z.flat), dtype=np.float64,
                                   count=z.size).reshape(z.shape)
            error = float(np.max(np.abs(out.astype(np.float64) - expected)))
            if not math.isfinite(error) or error > max_abs_error:
                raise ValueError('Native precision budget exceeded; no fallback')
        return {'status': 'ok', 'backend': self.backend, 'values': out,
                'count': int(a.shape[0]), 'dtype': 'float32',
                'max_abs_error': error, 'reference_checked': max_abs_error is not None,
                'runtime_promoted': False, 'fallback_used': False}
