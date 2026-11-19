"""Explicit, bounded CPU pilot SDK. No implicit backend promotion or speedup claim."""
import math

from .core import Registry

MAX_BATCH = 65536
DEFAULT_DOMAIN = (-8.0, 8.0)


def reference(kernel, x):
    if kernel == 'silu':
        return x / (1.0 + math.exp(-x)) if x >= 0 else x * math.exp(x) / (1.0 + math.exp(x))
    if kernel == 'gelu':
        return 0.5 * x * (1.0 + math.erf(x / math.sqrt(2.0)))
    raise ValueError('Unsupported kernel')


class CPUPilot:
    """Reference or pinned Python-ledger compute; both are scalar and CPU-only."""

    def __init__(self, backend='reference', domain=DEFAULT_DOMAIN, max_abs_error=None):
        if backend not in ('reference', 'python-ledger'):
            raise ValueError('Unsupported backend (native is experimental, not enabled)')
        if (not isinstance(domain, (tuple, list)) or len(domain) != 2 or
                any(type(v) not in (int, float) or not math.isfinite(v) for v in domain) or
                domain[0] >= domain[1]):
            raise ValueError('Invalid finite domain')
        if max_abs_error is not None and (
                type(max_abs_error) not in (int, float) or
                not math.isfinite(max_abs_error) or max_abs_error < 0):
            raise ValueError('Invalid error tolerance')
        self.backend = backend
        self.domain = tuple(domain)
        self.max_abs_error = max_abs_error
        self._registry = Registry() if backend == 'python-ledger' else None

    def compute(self, kernel, values):
        if kernel not in ('silu', 'gelu'):
            raise ValueError('Unsupported kernel')
        if not isinstance(values, (list, tuple)) or len(values) > MAX_BATCH:
            raise ValueError('Expected list/tuple with at most 65536 elements')
        if any(type(x) not in (int, float) or not math.isfinite(x) or
               not self.domain[0] <= x <= self.domain[1] for x in values):
            raise ValueError('Inputs must be finite numbers inside configured domain')
        output = []
        max_error = 0.0
        for x in values:
            ref = reference(kernel, x)
            val = ref if self._registry is None else self._registry.compute(kernel, x)
            if not math.isfinite(val):
                raise ValueError('Non-finite output')
            err = abs(val - ref)
            if not math.isfinite(err):
                raise ValueError('Non-finite error')
            max_error = max(max_error, err)
            if self.max_abs_error is not None and err > self.max_abs_error:
                raise ValueError('Error budget exceeded; no silent fallback')
            output.append(val)
        return {'status': 'ok', 'kernel': kernel, 'backend': self.backend,
                'values': output, 'max_abs_error': max_error,
                'domain': list(self.domain), 'count': len(output),
                'fallback_used': False}
