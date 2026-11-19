import json
import math
import unittest

from scripts.bench_end_to_end import run_benchmark


class EndToEndBenchmarkTests(unittest.TestCase):
    def test_report_has_finite_timings_and_errors(self):
        result = run_benchmark(samples=9, repeats=2, warmups=0)
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["samples"], 9)
        for name in ("silu", "gelu"):
            kernel = result["kernels"][name]
            self.assertGreater(kernel["median_ns_per_request"], 0)
            self.assertTrue(math.isfinite(kernel["max_abs_error"]))
            self.assertLess(kernel["max_abs_error"], 3e-5)
        json.dumps(result, allow_nan=False)

    def test_bounded_arguments(self):
        for kwargs in ({"samples": 1}, {"samples": 100001},
                       {"repeats": 0}, {"repeats": 101},
                       {"warmups": -1}, {"warmups": 101}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                run_benchmark(**kwargs)


if __name__ == "__main__":
    unittest.main()
