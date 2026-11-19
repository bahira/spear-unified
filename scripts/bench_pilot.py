"""Small, reproducible pilot SDK benchmark; not a production speedup claim."""
import json
import platform
import statistics
import time

from spear.pilot import CPUPilot


def measure(kernel, size, repeats=7):
    xs = [-8.0 + 16.0 * i / max(1, size - 1) for i in range(size)]
    pilots = {'reference': CPUPilot('reference'), 'python-ledger': CPUPilot('python-ledger')}
    for p in pilots.values():
        p.compute(kernel, xs)
    times = {k: [] for k in pilots}
    errors = {}
    for rep in range(repeats):
        order = list(pilots) if rep % 2 == 0 else list(reversed(pilots))
        for name in order:
            start = time.perf_counter_ns()
            result = pilots[name].compute(kernel, xs)
            times[name].append(time.perf_counter_ns() - start)
            errors[name] = result['max_abs_error']
    medians = {k: statistics.median(v) for k, v in times.items()}
    return {'kernel': kernel, 'size': size, 'median_ns_per_batch': medians,
            'ledger_to_reference_time_ratio': medians['python-ledger'] / medians['reference'],
            'max_abs_error': errors,
            'raw_ns_per_batch': times}


def main():
    report = {'status': 'ok', 'python': platform.python_version(),
              'platform': platform.platform(), 'repeats': 7,
              'sizes': [1, 64, 4096],
              'method': 'Same CPUPilot API; explicit backend; alternating order; full input validation, reference error calculation, output list and result dict',
              'limitations': 'Shared CI CPU; no native backend or WASM; short noisy microbenchmark; no speedup claim',
              'results': [measure(kernel, size) for kernel in ('silu', 'gelu') for size in (1, 64, 4096)]}
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
