"""Contract tests: two-layer optional SpearVM MLP, numeric fail-closed behavior."""
import math
import unittest
from unittest.mock import patch

from spear.spearvm import SpearVMPackedMLP, cpu_supported


class PackedMLPContractTests(unittest.TestCase):
    def test_import_does_not_load_native(self):
        # This module imported SpearVMPackedMLP before test; no optional
        # dependency is required just to import the class.
        self.assertTrue(callable(SpearVMPackedMLP))

    def test_host_guard_precedes_optional_import(self):
        with patch('spear.spearvm.cpu_supported', return_value=False):
            with patch('spear.spearvm.importlib.import_module') as importer:
                with self.assertRaisesRegex(RuntimeError, 'AVX2'):
                    SpearVMPackedMLP([([[1]], [0]), ([[1]], [0])])
                importer.assert_not_called()

    def test_budget_and_layer_count_rejected(self):
        for layers in ([], [([[1]], [0])], [1, 2], [1, 2, 3, 4, 5]):
            with self.subTest(layers=layers), self.assertRaises(ValueError):
                SpearVMPackedMLP(layers)
        with self.assertRaises(ValueError):
            SpearVMPackedMLP([([[1]], [0]), ([[1]], [0])], max_elements=True)

    def test_optional_missing_fails_explicitly(self):
        with patch('spear.spearvm.cpu_supported', return_value=True):
            with patch('spear.spearvm.importlib.import_module',
                       side_effect=ImportError('not installed')):
                with self.assertRaisesRegex(RuntimeError, 'unavailable'):
                    SpearVMPackedMLP([([[1]], [0]), ([[1]], [0])])

    def test_native_output_and_quality_when_installed(self):
        if not cpu_supported():
            self.skipTest('Linux x86 AVX2/FMA not present')
        try:
            import numpy as np
            import spur_math.nn
        except ImportError:
            self.skipTest('Optional installed native SpearVM missing')
        rng = np.random.default_rng(2026)
        params = [
            (rng.normal(0, .02, (128, 64)).astype('float32'),
             rng.normal(0, .01, 128).astype('float32')),
            (rng.normal(0, .02, (10, 128)).astype('float32'),
             rng.normal(0, .01, 10).astype('float32')),
        ]
        model = SpearVMPackedMLP(params)
        self.assertEqual(model.input_width, 64)
        self.assertEqual(model.output_width, 10)
        self.assertFalse(model.runtime_promoted)
        x = rng.normal(size=(32, 64)).astype('float32')
        out = model.compute(x, max_abs_error=.005)
        self.assertEqual(out['values'].shape, (32, 10))
        self.assertLess(out['max_abs_error'], .005)
        self.assertTrue(out['reference_checked'])
        self.assertFalse(out['runtime_promoted'])
        self.assertFalse(out['fallback_used'])
        for invalid in (np.ones((2, 65)), np.full((1, 64), math.nan),
                        np.zeros((2049, 64), dtype='float32')):
            with self.subTest(shape=np.asarray(invalid).shape), self.assertRaises(ValueError):
                model.compute(invalid)
        for tolerance in (-1, math.inf, True, '1e-6'):
            with self.subTest(tolerance=tolerance), self.assertRaises(ValueError):
                model.compute(x, max_abs_error=tolerance)

    def test_benchmark_quality_guard(self):
        try:
            import numpy as np
        except ImportError:
            self.skipTest('NumPy not installed')
        from scripts.bench_digits_mlp import compare_outputs
        gold = np.array([[2, 0], [0, 2]], dtype=np.float32)
        good = np.array([[2.0001, 0], [0, 1.9999]], dtype=np.float32)
        self.assertEqual(compare_outputs({'good': good}, gold, np)['good']['prediction_agreement_vs_torch'], 1)
        with self.assertRaisesRegex(ValueError, 'budget'):
            compare_outputs({'bad': np.array([[0, 2], [0, 2]], dtype=np.float32)}, gold, np)
        with self.assertRaises(ValueError):
            compare_outputs({'bad_dtype': gold.astype(np.float64)}, gold, np)


if __name__ == '__main__':
    unittest.main()
