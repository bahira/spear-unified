"""Offline precision and composition gates: reject rather than promote."""
import math
import unittest

from spear.quality import (
    MAX_PROBES, audit_composition, audit_ledger, evaluate_tree_f32, round_f32
)


class QualityGateTests(unittest.TestCase):
    def test_loose_f64_ledger_budget_passes_without_promotion(self):
        for kernel in ('silu', 'gelu'):
            out = audit_ledger(kernel, domain=(-8, 8), probes=257,
                               arithmetic='python-f64', abs_tol=1.0)
            self.assertEqual(out['status'], 'pass')
            self.assertEqual(out['checked'], 257)
            self.assertFalse(out['backend_promoted'])
            self.assertFalse(out['native_parity_verified'])
            self.assertFalse(out['samples_certify_domain'])

    def test_f32_step_rounding_audit_is_not_native_parity(self):
        out = audit_ledger('silu', domain=(-8, 8), probes=129,
                           arithmetic='emulated-f32-step-rounded', abs_tol=1)
        self.assertEqual(out['status'], 'pass')
        self.assertFalse(out['native_parity_verified'])
        self.assertEqual(out['arithmetic'], 'emulated-f32-step-rounded')

    def test_strict_error_rejects_approximation(self):
        out = audit_ledger('gelu', domain=(-1, 1), probes=33,
                           abs_tol=0, rel_tol=0)
        self.assertEqual(out['status'], 'reject')
        self.assertGreater(out['failed'], 0)
        self.assertGreater(out['max_abs_error'], 0)
        self.assertFalse(out['backend_promoted'])

    def test_f32_overflow_and_nonfinite_rejected(self):
        for x in (math.inf, math.nan, 1e100):
            with self.subTest(x=x), self.assertRaises(ValueError):
                round_f32(x)

    def test_protected_division_near_zero_is_explicit(self):
        tree = {'o': 'pdiv', 'c': [
            {'o': 'const', 'v': 1}, {'o': 'var', 'n': 'x'}]}
        self.assertEqual(evaluate_tree_f32(tree, 0.0), 1e4)
        self.assertEqual(evaluate_tree_f32(tree, -1e-6), -1e4)
        self.assertEqual(evaluate_tree_f32(tree, 1e-6), 1e4)

    def test_invalid_tree_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_tree_f32({'o': 'eval', 'c': []}, 1)

    def test_composition_identity_and_degradation(self):
        sigmoid = lambda x: 1/(1+math.exp(-x))
        logit = lambda y: math.log(y/(1-y))
        good = audit_composition(sigmoid, logit, domain=(-4, 4),
                                 probes=257, abs_tol=1e-12)
        self.assertEqual(good['status'], 'pass')
        bad = audit_composition(sigmoid, lambda y: 0,
                                domain=(-4, 4), probes=257, abs_tol=0.1)
        self.assertEqual(bad['status'], 'reject')
        self.assertGreater(bad['failed'], 0)

    def test_rejects_invalid_budgets_and_domains(self):
        for domain in ((0, 0), (1, -1), (0, math.nan), [1], ('0', 1)):
            with self.subTest(domain=domain), self.assertRaises(ValueError):
                audit_ledger('gelu', domain=domain, abs_tol=1)
        for tol in (-1, math.inf, math.nan, True, '0'):
            with self.subTest(tol=tol), self.assertRaises(ValueError):
                audit_ledger('gelu', abs_tol=tol)
        for probes in (0, 2, MAX_PROBES+1, 1.1, True):
            with self.subTest(probes=probes), self.assertRaises(ValueError):
                audit_ledger('gelu', probes=probes, abs_tol=1)
        with self.assertRaises(ValueError):
            audit_ledger('sin', abs_tol=1)
        with self.assertRaises(ValueError):
            audit_ledger('gelu', arithmetic='native', abs_tol=1)

    def test_nonfinite_composition_rejects_instead_of_crashing(self):
        out = audit_composition(lambda x: math.nan, lambda x: x,
                                domain=(-1, 1), abs_tol=1e-6)
        self.assertEqual(out['status'], 'reject')
        self.assertEqual(out['reason'], 'nonfinite_or_invalid')
        self.assertFalse(out['backend_promoted'])


if __name__ == '__main__':
    unittest.main()
