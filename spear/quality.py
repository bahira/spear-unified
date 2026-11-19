"""Fail-closed offline candidate-quality audits inspired by historical SPEAR papers.

These gates never select or promote a runtime backend. float32 mode rounds after
each AST operation in Python and is NOT proof of native C/AVX IEEE behavior:
compiler flags, FMA, transcendental routines, subnormals and the target ABI
still require native cross-backend parity testing.
"""
import math
import struct

from .core import OPS, Registry, validate_tree
from .pilot import reference

MAX_PROBES = 8193
SUPPORTED_KERNELS = frozenset(('silu', 'gelu'))


def round_f32(value):
    """IEEE-754 binary32 round-trip; reject overflow/nonfinite values."""
    try:
        value = float(value)
        if not math.isfinite(value):
            raise ValueError('Non-finite float32 intermediate')
        packed = struct.pack('!f', value)
        result = struct.unpack('!f', packed)[0]
    except (OverflowError, TypeError, struct.error) as exc:
        raise ValueError('Float32 conversion failed') from exc
    if not math.isfinite(result):
        raise ValueError('Non-finite float32 intermediate')
    return result


def evaluate_tree_f32(tree, x):
    """Emulate rounding at each whitelisted expression node, not full C semantics."""
    validate_tree(tree)
    x = round_f32(x)

    def walk(node):
        op = node['o']
        if op == 'var':
            return x
        if op == 'const':
            return round_f32(node['v'])
        arity, fn = OPS[op]
        args = [walk(c) for c in node['c']]
        if len(args) != arity:
            raise ValueError('Invalid operation arity')
        try:
            return round_f32(fn(*args))
        except (OverflowError, ZeroDivisionError, ValueError) as exc:
            raise ValueError('Invalid float32 computation') from exc

    return walk(tree)


def _finite_domain(domain, probes):
    if (not isinstance(domain, (tuple, list)) or len(domain) != 2 or
            any(type(v) not in (int, float) or not math.isfinite(v) for v in domain) or
            domain[0] >= domain[1]):
        raise ValueError('Invalid finite domain')
    if type(probes) is not int or not 3 <= probes <= MAX_PROBES:
        raise ValueError('Probes must be an integer between 3 and 8193')
    a, b = domain
    return [a + (b - a) * i / (probes - 1) for i in range(probes)]


def _tolerance(abs_tol, rel_tol):
    for item in (abs_tol, rel_tol):
        if type(item) not in (int, float) or not math.isfinite(item) or item < 0:
            raise ValueError('Tolerance must be finite and nonnegative')


def _scores(points, target, candidate, abs_tol, rel_tol):
    errors = []
    failed = 0
    max_error = -1.0
    worst_x = None
    for x in points:
        try:
            expected = target(x)
            actual = candidate(x)
            if not math.isfinite(expected) or not math.isfinite(actual):
                raise ValueError('Non-finite output')
            err = abs(actual - expected)
            if not math.isfinite(err):
                raise ValueError('Non-finite error')
        except (ValueError, OverflowError, ArithmeticError, TypeError):
            # Fail closed: malformed candidates must never be silently promoted.
            return {'status': 'reject', 'reason': 'nonfinite_or_invalid',
                    'checked': len(errors), 'failed': len(points) - len(errors),
                    'max_abs_error': None, 'worst_x': x}
        errors.append(err)
        if err > max_error:
            max_error, worst_x = err, x
        if err > abs_tol + rel_tol * abs(expected):
            failed += 1
    return {'status': 'pass' if failed == 0 else 'reject',
            'reason': None if failed == 0 else 'error_budget',
            'checked': len(errors), 'failed': failed,
            'max_abs_error': max_error, 'worst_x': worst_x}


def audit_ledger(kernel, *, domain=(-8.0, 8.0), probes=1025,
                 arithmetic='python-f64', abs_tol, rel_tol=0.0):
    """Audit pinned ledger kernel vs independent libm reference on a bounded grid.

    Pure-Python diagnostic only. A grid is NOT a continuous-domain certificate.
    """
    if kernel not in SUPPORTED_KERNELS:
        raise ValueError('Unsupported kernel')
    if arithmetic not in ('python-f64', 'emulated-f32-step-rounded'):
        raise ValueError('Unsupported arithmetic')
    _tolerance(abs_tol, rel_tol)
    points = _finite_domain(domain, probes)
    registry = Registry()
    if arithmetic == 'python-f64':
        candidate = lambda x: registry.compute(kernel, x)
    else:
        tree = registry.records[kernel]['tree']
        candidate = lambda x: evaluate_tree_f32(tree, x)
    report = _scores(points, lambda x: reference(kernel, x),
                     candidate, abs_tol, rel_tol)
    return dict(report, kernel=kernel, arithmetic=arithmetic,
                domain=list(domain), abs_tol=abs_tol, rel_tol=rel_tol,
                ledger_source_commit=registry.source.get('commit'),
                ledger_source_sha256=registry.source['sha256'][kernel],
                max_probes=MAX_PROBES, samples_certify_domain=False,
                native_parity_verified=False, backend_promoted=False)


def audit_composition(first, second, *, domain, probes=257, abs_tol,
                      rel_tol=0.0, target=None):
    """Check second(first(x)) against an identity/target on a bounded grid.

    This detects inverse-pair drift (e.g. sigmoid/logit), not safety globally.
    """
    if not callable(first) or not callable(second) or (target is not None and not callable(target)):
        raise ValueError('Functions must be callable')
    _tolerance(abs_tol, rel_tol)
    points = _finite_domain(domain, probes)
    score = _scores(points, target or (lambda x: x),
                    lambda x: second(first(x)), abs_tol, rel_tol)
    return dict(score, kind='composition', domain=list(domain),
                abs_tol=abs_tol, rel_tol=rel_tol,
                samples_certify_domain=False, backend_promoted=False)
