"""Pilot SDK contract and numerical safety tests."""
import math
import unittest

from spear.pilot import CPUPilot, reference


class PilotTests(unittest.TestCase):
    def test_reference_scalar(self):
        p = CPUPilot()
        for kernel in ('silu', 'gelu'):
            out = p.compute(kernel, [-8, -1, 0, 1, 8])
            self.assertEqual(out['backend'], 'reference')
            self.assertEqual(out['max_abs_error'], 0)
            self.assertEqual(out['count'], 5)
            self.assertEqual(out['values'], [reference(kernel, x) for x in [-8, -1, 0, 1, 8]])

    def test_ledger_error_is_measured(self):
        p = CPUPilot(backend='python-ledger')
        for kernel in ('silu', 'gelu'):
            xs = [-8 + i / 16 for i in range(257)]
            out = p.compute(kernel, xs)
            self.assertEqual(out['count'], len(xs))
            self.assertEqual(out['backend'], 'python-ledger')
            self.assertEqual(out['max_abs_error'], max(abs(a - reference(kernel, x)) for a, x in zip(out['values'], xs)))
            self.assertFalse(out['fallback_used'])

    def test_error_budget_fail_closed(self):
        with self.assertRaisesRegex(ValueError, 'Error budget exceeded'):
            CPUPilot('python-ledger', max_abs_error=0).compute('gelu', [1.0])

    def test_invalid_backend_and_domain(self):
        for backend in ('native', 'wasm', 'auto', ''):
            with self.subTest(backend=backend), self.assertRaises(ValueError):
                CPUPilot(backend)
        for domain in ((0, 0), (1, -1), (0, math.inf), ('0', 1), [0], [0, 1, 2]):
            with self.subTest(domain=domain), self.assertRaises(ValueError):
                CPUPilot(domain=domain)
        for tolerance in (-1, math.nan, math.inf, '0', True):
            with self.subTest(tolerance=tolerance), self.assertRaises(ValueError):
                CPUPilot(max_abs_error=tolerance)

    def test_input_guards(self):
        p = CPUPilot()
        for values in ([math.nan], [math.inf], [-9], [9], [True], ['1'], [1 + 0j], '1', None, [0] * 65537):
            with self.subTest(kind=str(type(values)), count=len(values) if hasattr(values, '__len__') else None), self.assertRaises(ValueError):
                p.compute('silu', values)
        with self.assertRaises(ValueError):
            p.compute('sin', [1])
        self.assertEqual(p.compute('silu', [])['values'], [])


if __name__ == '__main__':
    unittest.main()
