"""Experimental SpearVM adapter: no implicit import and strict fail-closed guards."""
import math
import unittest
from unittest.mock import patch

from spear.spearvm import SpearVMPackedGELU, cpu_supported


class SpearVMAdapterTests(unittest.TestCase):
    def test_unsupported_host_rejects_before_import(self):
        with patch('spear.spearvm.cpu_supported', return_value=False):
            with patch('spear.spearvm.importlib.import_module') as importer:
                with self.assertRaisesRegex(RuntimeError, 'AVX2'):
                    SpearVMPackedGELU([[1]], [0])
                importer.assert_not_called()

    def test_optional_import_absent_fails_closed(self):
        with patch('spear.spearvm.cpu_supported', return_value=True):
            with patch('spear.spearvm.importlib.import_module', side_effect=ImportError('missing')):
                with self.assertRaisesRegex(RuntimeError, 'unavailable'):
                    SpearVMPackedGELU([[1]], [0])

    def test_invalid_config_never_loads_native(self):
        with self.assertRaises(ValueError):
            SpearVMPackedGELU([[1]], [0], max_elements=0)

    def test_cpu_supported_is_boolean(self):
        self.assertIsInstance(cpu_supported(), bool)

    def test_real_backend_when_installed(self):
        if not cpu_supported():
            self.skipTest('AVX2/FMA Linux host unavailable')
        try:
            import numpy as np
            import spur_math
        except ImportError:
            self.skipTest('Optional native SpearVM and NumPy not installed')
        weights = (np.arange(128*64, dtype=np.float32).reshape(128, 64) % 31 - 15) * 0.001
        bias = np.linspace(-0.02, 0.02, 128, dtype=np.float32)
        adapter = SpearVMPackedGELU(weights, bias)
        self.assertFalse(adapter.runtime_promoted)
        x = np.linspace(-1, 1, 5*64, dtype=np.float32).reshape(5, 64)
        out = adapter.compute(x, max_abs_error=1e-3)
        self.assertEqual(out['values'].shape, (5, 128))
        self.assertEqual(out['dtype'], 'float32')
        self.assertTrue(out['reference_checked'])
        self.assertLessEqual(out['max_abs_error'], 1e-3)
        self.assertFalse(out['runtime_promoted'])
        self.assertFalse(out['fallback_used'])
        for bad in (np.ones((5, 65)), np.array([[math.nan]*64]), [[1]*64]*5000):
            with self.assertRaises(ValueError):
                adapter.compute(bad)
        with self.assertRaises(ValueError):
            adapter.compute(x, max_abs_error=-1)
        with self.assertRaises(ValueError):
            adapter.compute(x, max_abs_error=0)


if __name__ == '__main__':
    unittest.main()
