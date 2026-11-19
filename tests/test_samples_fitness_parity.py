"""Search fitness must measure the simplified tree actually returned to users."""
import test_samples_coverage as coverage
import unittest
import shutil
import subprocess
import json

@unittest.skipUnless(shutil.which('node'),'Node required')
class SamplesFitnessParityChecks(unittest.TestCase):
    setUp = coverage.SamplesCoverageChecks.setUp

    def run_constant(self, value):
        data={name:[{'x':i+shift,'y':value} for i in range(8)]
              for name,shift in [('train',0),('validation',.25)]}
        path=self.root/'synthetic.json';path.write_text(json.dumps(data))
        p=subprocess.run(['node','--disable-warning=MODULE_TYPELESS_PACKAGE_JSON',
                          str(self.root/'scripts/discover_samples.mjs'),str(path)],
                         cwd=self.root,capture_output=True,text=True,timeout=5,check=True)
        return json.loads(p.stdout)

    def assert_parity(self,r):
        m=r['training_objective']
        expected=-(r['splits']['train']['candidate']['mse']+m['complexity_cost'])
        self.assertAlmostEqual(m['best_fitness'],expected,delta=1e-18)
        self.assertFalse(r['registry_updated'])

    def test_rounded_constant_must_not_claim_zero_training_error(self):
        r=self.run_constant(.123456789)
        self.assertGreater(r['splits']['train']['candidate']['mse'],1e-16)
        self.assert_parity(r)

    def test_exact_constant_parity(self):
        r=self.run_constant(1)
        self.assertEqual(r['splits']['train']['candidate']['mse'],0)
        self.assert_parity(r)

    def test_default_demo_parity(self):
        p=subprocess.run(['node','--disable-warning=MODULE_TYPELESS_PACKAGE_JSON',
                          str(self.root/'scripts/discover_samples.mjs')],cwd=self.root,
                         capture_output=True,text=True,timeout=5,check=True)
        self.assert_parity(json.loads(p.stdout))
