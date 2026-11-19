"""Narrow-coordinate sample search must not lose affine signal in scaling."""
import unittest
import shutil
import json
import subprocess
import test_samples_coverage as coverage

@unittest.skipUnless(shutil.which('node'),'Node required')
class SamplesGPScalingChecks(unittest.TestCase):
    setUp=coverage.SamplesCoverageChecks.setUp

    def run_samples(self, offset, step, slope, constant=False):
        data={name:[{'x':offset+step*(i+shift),
                     'y':1 if constant else 1+slope*step*(i+shift)} for i in range(8)]
              for name,shift in [('train',0),('validation',.25)]}
        path=self.root/'synthetic.json';path.write_text(json.dumps(data))
        p=subprocess.run(['node','--disable-warning=MODULE_TYPELESS_PACKAGE_JSON',
                         str(self.root/'scripts/discover_samples.mjs'),str(path)],
                         cwd=self.root,capture_output=True,text=True,timeout=5,check=True)
        return json.loads(p.stdout)

    def test_tiny_range_high_slope(self):
        r=self.run_samples(0,1e-9,2e8)
        self.assertLess(r['splits']['validation']['candidate']['max_abs_error'],1e-6)

    def test_offset_narrow_range(self):
        r=self.run_samples(9999,1e-4,5)
        self.assertLess(r['splits']['validation']['candidate']['max_abs_error'],1e-7)

    def test_constant_prediction_remains_supported(self):
        r=self.run_samples(0,1,2,True)
        self.assertEqual(r['splits']['validation']['candidate']['mse'],0)
        self.assertEqual(r['training_objective']['best_fitness'],
                         -r['training_objective']['complexity_cost'])
