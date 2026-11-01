import math
import shutil
import unittest
from spear.discovery import discover

@unittest.skipUnless(shutil.which('node'), 'Node required for search integration')
class DiscoveryChecks(unittest.TestCase):
    def test_actual_search_reproducible_and_independent_reference(self):
        task={'formula':'x*x','seed':42}
        a,b=discover(task),discover(task)
        self.assertEqual(a['status'],'ok')
        self.assertTrue(a['accepted_on_probe'])
        self.assertFalse(a['registry_updated'])
        self.assertEqual(a['tree'],b['tree'])
        self.assertEqual(a['holdout'],b['holdout'])
        self.assertEqual(a['holdout']['max_abs_error'],0)
        from spear.core import compile_tree
        fn=compile_tree(a['tree'])
        for x in [-2,-1.2345,0,0.12345,1.71,2]:
            self.assertAlmostEqual(fn(x),math.pow(x,2),places=13)

    def test_inaccurate_candidate_rejected(self):
        r=discover({'formula':'sin(x)'})
        self.assertFalse(r['accepted_on_probe'])
        self.assertFalse(r['registry_updated'])

    def test_budget_and_domain_validation(self):
        for task in [{'formula':'x','rows':100000}, {'formula':'x','generations':0},
                     {'formula':'x','lo':2,'hi':1},{'formula':'x','seed':True},
                     {'formula':'x','hi':float('nan')}]:
            with self.assertRaises(ValueError):discover(task)

    def test_timeout(self):
        from unittest.mock import patch
        import subprocess
        with patch('spear.discovery.subprocess.run',side_effect=subprocess.TimeoutExpired('node',5)):
            self.assertEqual(discover({'formula':'x'})['status'],'timeout')

    def test_parse_failure_is_not_candidate(self):
        self.assertEqual(discover({'formula':'not_a_function(x)'})['status'],'error')
