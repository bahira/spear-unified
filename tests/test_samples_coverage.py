"""Range/extrapolation reporting for synthetic supplied samples in isolated roots."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

@unittest.skipUnless(shutil.which('node'),'Node required for samples CLI')
class SamplesCoverageChecks(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory(prefix='spear-coverage-test-')
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        (self.root/'scripts').mkdir();(self.root/'reports').mkdir()
        (self.root/'spear/data').mkdir(parents=True)
        shutil.copy2(ROOT/'scripts/discover_samples.mjs',self.root/'scripts')
        shutil.copytree(ROOT/'vendor/superspear',self.root/'vendor/superspear')
        shutil.copy2(ROOT/'spear/data/source.json',self.root/'spear/data')

    def run_samples(self,xs):
        data={name:[{'x':x,'y':x*x+1} for x in values] for name,values in xs.items()}
        path=self.root/'synthetic.json';path.write_text(json.dumps(data))
        p=subprocess.run(['node','--disable-warning=MODULE_TYPELESS_PACKAGE_JSON',
                          str(self.root/'scripts/discover_samples.mjs'),str(path)],
                         cwd=self.root,capture_output=True,text=True,timeout=5)
        self.assertEqual(p.returncode,0,p.stderr)
        return json.loads(p.stdout)

    def test_mixed_heldout_ranges_are_flagged(self):
        r=self.run_samples({'train':list(range(8)),
            'validation':[-2,-1,0.25,0.75,3.25,6.75,8,9],
            'test':[-3,-0.5,0.5,1.5,2.5,4.5,7.5,10]})
        self.assertEqual(r['training_domain'],[0,7])
        for name,domain in [('validation',[-2,9]),('test',[-3,10])]:
            c=r['split_coverage'][name]
            self.assertEqual(c['domain'],domain)
            self.assertEqual(c['below_training'],2)
            self.assertEqual(c['above_training'],2)
            self.assertEqual(c['outside_training'],4)
            self.assertTrue(c['extrapolation'])
        self.assertEqual(r['split_coverage']['train']['outside_training'],0)
        self.assertFalse(r['registry_updated'])
        md=(self.root/'reports/samples-discovery.md').read_text()
        self.assertIn('extrapolation',md.lower())
        self.assertIn('4/8',md)

    def test_inside_range_is_not_labeled_extrapolation(self):
        r=self.run_samples({'train':list(range(8)),
            'validation':[0.25,0.5,0.75,1.25,1.5,1.75,2.25,2.5],
            'test':[2.75,3.25,3.5,3.75,4.25,4.5,4.75,5.25]})
        for c in r['split_coverage'].values():
            self.assertEqual(c['outside_training'],0)
            self.assertFalse(c['extrapolation'])

    def test_optional_test_split_is_not_invented(self):
        r=self.run_samples({'train':list(range(8)),'validation':list(range(8,16))})
        self.assertNotIn('test',r['split_coverage'])
        self.assertEqual(r['split_coverage']['validation']['outside_training'],8)
        self.assertTrue(r['split_coverage']['validation']['extrapolation'])
