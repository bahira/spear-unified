"""Separate interpolation and extrapolation errors without changing fitting."""
import test_samples_coverage as coverage
import unittest
import shutil
import json
import math
import subprocess


@unittest.skipUnless(shutil.which("node"), "Node required for samples CLI")
class SamplesRangeMetricsChecks(unittest.TestCase):
    setUp = coverage.SamplesCoverageChecks.setUp
    run_samples = coverage.SamplesCoverageChecks.run_samples

    def run_shifted(self, shift):
        data = {'train': [{'x': x, 'y': x*x+1} for x in range(8)],
                'validation': [{'x': x, 'y': x*x+1+(shift if x < 0 or x > 7 else 0)}
                               for x in [-2,-1,.25,.75,3.25,6.75,8,9]]}
        path = self.root/'synthetic.json'
        path.write_text(json.dumps(data))
        p = subprocess.run(['node','--disable-warning=MODULE_TYPELESS_PACKAGE_JSON',
                            str(self.root/'scripts/discover_samples.mjs'),str(path)],
                           cwd=self.root,capture_output=True,text=True,timeout=5)
        self.assertEqual(p.returncode,0,p.stderr)
        return json.loads(p.stdout)

    def test_group_errors_reconstruct_global_mse(self):
        r = self.run_shifted(1000)
        groups = r['range_metrics']['validation']
        for model in ['candidate','affine_baseline','quadratic_baseline']:
            inside, outside = [groups[g][model] for g in ['inside_training','outside_training']]
            self.assertEqual((inside['n'],outside['n']),(4,4))
            self.assertTrue(all(math.isfinite(v) for m in [inside,outside] for v in m.values()))
            self.assertGreater(outside['rmse'],100)
            self.assertAlmostEqual((inside['mse']+outside['mse'])/2,
                                   r['splits']['validation'][model]['mse'],places=7)
        self.assertIn('outside_training', (self.root/'reports/samples-discovery.md').read_text())

    def test_empty_groups_are_null_and_optional_test_absent(self):
        r = self.run_samples({'train':list(range(8)),'validation':list(range(8,16))})
        self.assertIsNone(r['range_metrics']['train']['outside_training'])
        self.assertIsNone(r['range_metrics']['validation']['inside_training'])
        self.assertNotIn('test',r['range_metrics'])

    def test_heldout_labels_do_not_change_fitting(self):
        a,b = self.run_shifted(0),self.run_shifted(1000)
        for key in ['candidate','baseline','quadratic_baseline']:
            self.assertEqual(a[key],b[key])
        self.assertNotEqual(a['range_metrics']['validation']['outside_training'],
                            b['range_metrics']['validation']['outside_training'])
