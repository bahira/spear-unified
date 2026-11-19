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
        self.assertTrue(a['source_files_verified'])
        self.assertEqual(set(a['source_file_sha256']), {'engine.ts', 'math-utils.ts'})
        self.assertTrue(a['accepted_on_probe'])
        self.assertFalse(a['registry_updated'])
        self.assertEqual(a['tree'],b['tree'])
        self.assertEqual(a['holdout'],b['holdout'])
        self.assertEqual(a['holdout']['max_abs_error'],0)
        self.assertEqual(a['holdout']['rows'],257)
        self.assertTrue(a['holdout']['endpoints_included'])
        self.assertTrue(a['holdout']['midpoints_included'])
        self.assertEqual(a['holdout']['base_rows'],129)
        self.assertEqual(a['holdout']['midpoint_rows'],128)
        from spear.core import compile_tree
        fn=compile_tree(a['tree'])
        for x in [-2,-1.2345,0,0.12345,1.71,2]:
            self.assertAlmostEqual(fn(x),math.pow(x,2),places=13)

    def test_inaccurate_candidate_rejected(self):
        r=discover({'formula':'sin(x)'})
        self.assertFalse(r['accepted_on_probe'])
        self.assertFalse(r['registry_updated'])

    def test_endpoint_error_rejects_interior_only_false_positive(self):
        # On the previous interior-only grid seed 42 finds constant 1.032672:
        # max error ~0.166181 passes 0.167, but x=0.1 has error 0.167328.
        r=discover({'formula':'2*x+1','lo':0,'hi':0.1,'seed':42,
                    'max_abs_error':0.167})
        self.assertEqual(r['status'],'ok')
        from spear.core import compile_tree
        fn=compile_tree(r['tree'])
        endpoint_error=max(abs(fn(x)-(2*x+1)) for x in (0,0.1))
        self.assertGreater(endpoint_error,r['requested_max_abs_error'])
        self.assertFalse(r['accepted_on_probe'])
        self.assertGreaterEqual(r['holdout']['max_abs_error'],endpoint_error-1e-13)
        self.assertTrue(r['holdout']['endpoints_included'])
        self.assertEqual(r['holdout']['rows'],257)
        self.assertFalse(r['registry_updated'])

    def test_midpoint_probe_rejects_peak_hidden_between_base_points(self):
        # Synthetic counterexample: a peak lies between two old holdout points.
        left=-1+2*(63+0.271828)/127
        right=-1+2*(64+0.271828)/127
        center=(left+right)/2
        formula=f'exp(-1000000*(x-{center:.17g})*(x-{center:.17g}))'
        r=discover({'formula':formula,'lo':-1,'hi':1,'seed':42,
                    'max_abs_error':1e-4})
        self.assertEqual(r['status'],'ok')
        from spear.core import compile_tree
        fn=compile_tree(r['tree'])
        independent_error=abs(fn(center)-math.exp(0))
        self.assertGreater(independent_error,0.99)
        self.assertFalse(r['accepted_on_probe'])
        self.assertGreaterEqual(r['holdout']['max_abs_error'],independent_error-1e-12)
        self.assertTrue(r['holdout']['midpoints_included'])
        self.assertEqual(r['holdout']['base_rows'],129)
        self.assertEqual(r['holdout']['midpoint_rows'],128)
        self.assertEqual(r['holdout']['rows'],257)
        self.assertFalse(r['registry_updated'])

    def test_budget_and_domain_validation(self):
        for task in [{'formula':'x','rows':100000}, {'formula':'x','generations':0},
                     {'formula':'x','lo':2,'hi':1},{'formula':'x','seed':True},
                     {'formula':'x','hi':float('nan')}]:
            with self.assertRaises(ValueError):discover(task)

    def test_nonfinite_metrics_are_rejected(self):
        from unittest.mock import patch
        import json
        import subprocess
        record={'holdout':{'mse':float('inf'),'max_abs_error':0},'duration_ms':1}
        output=subprocess.CompletedProcess([],0,json.dumps(record),'')
        with patch('spear.discovery.subprocess.run',return_value=output):
            self.assertEqual(discover({'formula':'x'})['status'],'error')

    def test_vendor_integrity_checked(self):
        from unittest.mock import patch
        with patch('spear.discovery.hashlib.sha256') as digest:
            digest.return_value.hexdigest.return_value='invalid'
            with self.assertRaisesRegex(ValueError,'Vendor checksum mismatch'):
                discover({'formula':'x'})

    def test_timeout(self):
        from unittest.mock import patch
        import subprocess
        with patch('spear.discovery.subprocess.run',side_effect=subprocess.TimeoutExpired('node',5)):
            self.assertEqual(discover({'formula':'x'})['status'],'timeout')

    def test_parse_failure_is_not_candidate(self):
        self.assertEqual(discover({'formula':'not_a_function(x)'})['status'],'error')
