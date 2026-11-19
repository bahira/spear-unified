"""Reproducible end-to-end scalar CPU probe; no external dependencies or services.

Measures JSON decoding, dispatch, scalar evaluation and JSON encoding together.
Use --output to persist results; the default prints JSON only.
"""
import argparse
import json
import math
import platform
import statistics
import time

from spear.core import Router


def run_benchmark(samples=1001, repeats=7, warmups=2):
    if not 2 <= samples <= 100000 or not 1 <= repeats <= 100 or not 0 <= warmups <= 100:
        raise ValueError("Benchmark bounds exceeded")
    router = Router()
    xs = [-8.0 + 16.0 * i / (samples - 1) for i in range(samples)]
    report = {
        "schema_version": 1,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "samples": samples,
        "repeats": repeats,
        "warmups": warmups,
        "domain": [-8.0, 8.0],
        "method": "JSON encode request, decode request, dispatch compute, encode response",
        "limitations": "Single-process scalar microbenchmark; no network, deployment, batch-native or client traffic",
        "kernels": {},
    }
    for kernel in ("silu", "gelu"):
        def trial():
            start = time.perf_counter_ns()
            outputs = []
            for x in xs:
                payload = json.dumps({"kind": "compute", "kernel": kernel, "x": x})
                result = router.run(json.loads(payload))
                outputs.append(json.loads(json.dumps(result))["value"])
            elapsed = time.perf_counter_ns() - start
            return elapsed / samples, outputs

        for _ in range(warmups):
            trial()
        timings = []
        outputs = None
        for _ in range(repeats):
            ns, outputs = trial()
            timings.append(ns)
        if kernel == "silu":
            expected = [x / (1 + math.exp(-x)) for x in xs]
        else:
            expected = [0.5 * x * (1 + math.erf(x / math.sqrt(2))) for x in xs]
        errors = [abs(a - b) for a, b in zip(outputs, expected)]
        report["kernels"][kernel] = {
            "median_ns_per_request": statistics.median(timings),
            "min_ns_per_request": min(timings),
            "max_ns_per_request": max(timings),
            "max_abs_error": max(errors),
            "requests_per_second_median": 1e9 / statistics.median(timings),
        }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=1001)
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--output", help="Optional path for JSON results")
    args = parser.parse_args()
    report = run_benchmark(args.samples, args.repeats, args.warmups)
    payload = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(payload)
    print(payload, end="")


if __name__ == "__main__":
    main()
