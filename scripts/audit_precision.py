"""Explicit bounded precision audit CLI; never promotes runtime backends.

Examples:
python -m scripts.audit_precision --kernel gelu --dtype emulated-f32-step-rounded --abs-tol 0.001
python -m scripts.audit_precision --kernel silu --dtype python-f64 --abs-tol 0.01
"""
import argparse
import json

from spear.quality import audit_ledger


def main():
    parser = argparse.ArgumentParser(description='Check pinned ledger on independent reference grid')
    parser.add_argument('--kernel', choices=['silu', 'gelu'], required=True)
    parser.add_argument('--dtype', choices=['python-f64', 'emulated-f32-step-rounded'],
                        default='python-f64')
    parser.add_argument('--domain-min', type=float, default=-8.0)
    parser.add_argument('--domain-max', type=float, default=8.0)
    parser.add_argument('--probes', type=int, default=1025)
    parser.add_argument('--abs-tol', type=float, required=True)
    parser.add_argument('--rel-tol', type=float, default=0.0)
    args = parser.parse_args()
    result = audit_ledger(args.kernel, domain=(args.domain_min, args.domain_max),
                          probes=args.probes, arithmetic=args.dtype,
                          abs_tol=args.abs_tol, rel_tol=args.rel_tol)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0 if result['status'] == 'pass' else 2


if __name__ == '__main__':
    raise SystemExit(main())
