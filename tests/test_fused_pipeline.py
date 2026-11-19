"""Contract tests for the exact fused C experiment (no production backend)."""
import math
import platform
import shutil
import tempfile
import unittest

from scripts.bench_fused_pipeline import scalar, python_baseline, compile_native, native_list, benchmark


@unittest.skipUnless(platform.system() == 'Linux' and shutil.which('cc'), 'Linux C compiler required')
class FusedPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.fn = compile_native(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_domain_and_clamp_boundaries(self):
        for xs in ([], [-8, -1/6, 0, 1, 8], [-8 + i/64 for i in range(1025)]):
            expected = python_baseline(xs)
            actual = native_list(xs, self.fn)
            self.assertEqual(len(expected), len(actual))
            for a, b in zip(expected, actual):
                self.assertTrue(math.isfinite(b))
                self.assertAlmostEqual(a, b, delta=1e-12)

    def test_bounded_benchmark(self):
        report = benchmark(64, self.fn, repeats=3)
        self.assertEqual(report['size'], 64)
        self.assertGreater(report['median_ns_per_batch']['c_fused_list'], 0)
        self.assertGreater(report['median_ns_per_batch']['python'], 0)


if __name__ == '__main__':
    unittest.main()
