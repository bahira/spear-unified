"""Conclusions must reflect current held-out measurements, not canned numbers."""
import test_samples_coverage as coverage
import unittest
import shutil
import subprocess
import json

@unittest.skipUnless(shutil.which('node'), 'Node required')
class SamplesConclusionChecks(unittest.TestCase):
    setUp = coverage.SamplesCoverageChecks.setUp
    run_samples = coverage.SamplesCoverageChecks.run_samples

    def check_conclusion(self,r):
        c=r['conclusion']
        self.assertIn('No statistical significance',c)
        self.assertNotIn('train:',c)
        for name in ['validation','test']:
            if name not in r['splits']:
                self.assertNotIn(name+':',c)
                continue
            m=r['splits'][name]
            for model in ['candidate','quadratic_baseline']:
                self.assertIn(format(m[model]['rmse'],'.6g'),c)
            relation='lower' if m['candidate']['mse']<m['quadratic_baseline']['mse'] else ('higher' if m['candidate']['mse']>m['quadratic_baseline']['mse'] else 'equal')
            self.assertIn(name+': candidate RMSE is '+relation,c)
        self.assertIn(c,(self.root/'reports/samples-discovery.md').read_text())

    def test_supplied_samples_without_test(self):
        self.check_conclusion(self.run_samples({'train':list(range(8)), 'validation':list(range(8,16))}))

    def test_current_synthetic_metrics(self):
        p=subprocess.run(['node','--disable-warning=MODULE_TYPELESS_PACKAGE_JSON',
                          str(self.root/'scripts/discover_samples.mjs')],cwd=self.root,
                         capture_output=True,text=True,timeout=5,check=True)
        self.check_conclusion(json.loads(p.stdout))

    def test_changed_synthetic_generator_does_not_keep_old_numbers(self):
        script=self.root/'scripts/discover_samples.mjs'
        script.write_text(script.read_text().replace('y:1.75*x*x+0.4+noise()', 'y:2*x+0.4+noise()'))
        p=subprocess.run(['node','--disable-warning=MODULE_TYPELESS_PACKAGE_JSON',str(script)],
                         cwd=self.root,capture_output=True,text=True,timeout=5,check=True)
        self.check_conclusion(json.loads(p.stdout))
