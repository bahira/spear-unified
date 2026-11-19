"""Identify input bytes without persisting local file or directory names."""
import unittest
import shutil
import hashlib
import json
import subprocess
import test_samples_coverage as coverage

@unittest.skipUnless(shutil.which('node'),'Node required')
class SamplesInputIdentityChecks(unittest.TestCase):
    setUp=coverage.SamplesCoverageChecks.setUp

    def run_input(self, filename, delta=0):
        data={name:[{'x':i+shift,'y':(i+shift)**2+1+delta} for i in range(8)]
              for name,shift in [('train',0),('validation',.25)]}
        raw=json.dumps(data).encode()
        path=self.root/filename;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        p=subprocess.run(['node','--disable-warning=MODULE_TYPELESS_PACKAGE_JSON',
                          str(self.root/'scripts/discover_samples.mjs'),str(path)],
                         cwd=self.root,capture_output=True,text=True,check=True,timeout=5)
        r=json.loads(p.stdout)
        self.assertEqual(r['origin']['input_sha256'],hashlib.sha256(raw).hexdigest())
        self.assertEqual(r['origin']['input_bytes'],len(raw))
        for output in [p.stdout,(self.root/'reports/samples-discovery.json').read_text(),
                       (self.root/'reports/samples-discovery.md').read_text()]:
            self.assertNotIn(str(path),output)
            self.assertNotIn(filename,output)
        self.assertNotIn('path',r['origin'])
        self.assertIn(r['origin']['input_sha256'],(self.root/'reports/samples-discovery.md').read_text())
        return r

    def test_digest_matches_read_bytes_without_path(self):
        self.run_input('synthetic-private-path/measurements.json')

    def test_relocation_preserves_identity_and_results(self):
        a=self.run_input('first/data.json');b=self.run_input('second/renamed.json')
        self.assertEqual(a['origin'],b['origin'])
        self.assertEqual(a['candidate'],b['candidate'])
        self.assertEqual(a['splits'],b['splits'])

    def test_changed_measurements_change_identity(self):
        a=self.run_input('data.json');b=self.run_input('data.json',1)
        self.assertNotEqual(a['origin']['input_sha256'],b['origin']['input_sha256'])
