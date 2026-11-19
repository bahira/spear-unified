"""Affine reference must remain useful on narrow, offset coordinate ranges."""
import json
import shutil
import subprocess
import unittest
import test_samples_coverage as coverage

@unittest.skipUnless(shutil.which('node'), 'Node required')
class SamplesAffineStabilityChecks(unittest.TestCase):
    setUp = coverage.SamplesCoverageChecks.setUp

    def run_affine(self, offset, step):
        data = {name:[{'x':offset+step*(i+shift), 'y':2*step*(i+shift)+1}
                      for i in range(8)] for name,shift in [('train',0),('validation',.25)]}
        path=self.root/'synthetic.json';path.write_text(json.dumps(data))
        p=subprocess.run(['node','--disable-warning=MODULE_TYPELESS_PACKAGE_JSON',
                          str(self.root/'scripts/discover_samples.mjs'),str(path)],
                         cwd=self.root,capture_output=True,text=True,timeout=5)
        self.assertEqual(p.returncode,0,p.stderr)
        return json.loads(p.stdout)

    def test_large_offset_small_range(self):
        r=self.run_affine(9999,1e-4)
        self.assertLess(r['splits']['validation']['affine_baseline']['max_abs_error'],1e-10)

    def test_small_range_near_zero(self):
        r=self.run_affine(0,1e-9)
        self.assertLess(r['splits']['validation']['affine_baseline']['max_abs_error'],1e-14)

    def test_ordinary_range(self):
        r=self.run_affine(0,1)
        self.assertLess(r['splits']['validation']['affine_baseline']['max_abs_error'],1e-12)
