"""Independent, bounded precision probe; not a continuous error certificate."""
from array import array
import json
import math
import random
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.bench_native_bridge import BUDGET, build_bridge, native


def probe(fn):
    rng = random.Random(20261113)
    groups = {
        'seeded_uniform': [rng.uniform(-1, 1) for _ in range(4096)],
        'boundary_neighbors': [math.nextafter(b, direction)
                               for b in [-1., 0., 1.] for direction in [-math.inf, math.inf]] + [-1., -0., 1.],
        'extreme_fallback': [-sys.float_info.max, -1e100, -1e10, 1e10, 1e100, sys.float_info.max],
    }
    results = []
    for name, values in groups.items():
        xs = array('d', values)
        original = xs.tobytes()
        for tolerance in [0, BUDGET]:
            out, used = native(xs, fn, tolerance)
            errors = [abs(y-math.sin(x)) for x, y in zip(xs, out)]
            expected = sum(abs(x) <= 1 for x in xs) if tolerance == BUDGET else 0
            fallback = [(x, y) for x, y in zip(xs, out) if tolerance == 0 or abs(x) > 1]
            record = {'group': name, 'tolerance': tolerance, 'points': len(xs),
                      'approximated': used, 'expected_approximated': expected,
                      'max_abs_error': max(errors),
                      'fallback_matches_python_libm': all(y == math.sin(x) for x, y in fallback),
                      'input_unchanged': xs.tobytes() == original,
                      'negative_zero_preserved': all(math.copysign(1, y) == math.copysign(1, x)
                                                     for x, y in zip(xs, out) if x == 0)}
            if (used != expected or not all(math.isfinite(y) for y in out)
                    or record['max_abs_error'] > tolerance
                    or not all(record[k] for k in ['fallback_matches_python_libm', 'input_unchanged', 'negative_zero_preserved'])):
                raise ValueError(f'Precision/routing check failed: {record}')
            results.append(record)
    return results


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='spear-precision-') as directory:
        print(json.dumps({'seed': 20261113, 'results': probe(build_bridge(directory)),
                          'limits': 'Finite synthetic probes on this platform, not continuous certification; exact fallback agreement is platform-specific.'}, indent=2, allow_nan=False))
