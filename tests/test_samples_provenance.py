"""Run the samples CLI in disposable checkouts; never overwrite tracked reports."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

@unittest.skipUnless(shutil.which('node'),'Node required for samples CLI')
class SamplesProvenanceChecks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='spear-samples-provenance-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'scripts').mkdir()
        (self.root/'reports').mkdir()
        (self.root/'spear/data').mkdir(parents=True)
        shutil.copy2(ROOT/'scripts/discover_samples.mjs',self.root/'scripts')
        shutil.copytree(ROOT/'vendor/superspear',self.root/'vendor/superspear')
        shutil.copy2(ROOT/'spear/data/source.json',self.root/'spear/data')

    def run_samples(self):
        return subprocess.run(['node','--disable-warning=MODULE_TYPELESS_PACKAGE_JSON',
                               str(self.root/'scripts/discover_samples.mjs')],
                              cwd=self.root,capture_output=True,text=True,timeout=5)

    def test_unmodified_engine_reports_verified_provenance(self):
        p=self.run_samples()
        self.assertEqual(p.returncode,0,p.stderr)
        report=json.loads(p.stdout)
        self.assertTrue(report['source_files_verified'])
        expected=json.loads((self.root/'vendor/superspear/checksums.json').read_text())
        self.assertEqual(report['source_file_sha256'],expected)
        self.assertEqual(report['origin']['kind'],'synthetic_demo')
        self.assertFalse(report['registry_updated'])

    def test_modified_engine_rejected_before_module_execution(self):
        engine=self.root/'vendor/superspear/engine.ts'
        engine.write_text(engine.read_text()+"\nthrow new Error('UNVERIFIED_ENGINE_EXECUTED');\n")
        p=self.run_samples()
        self.assertNotEqual(p.returncode,0)
        self.assertIn('Vendor checksum mismatch: engine.ts',p.stderr)
        self.assertNotIn('UNVERIFIED_ENGINE_EXECUTED',p.stderr)
        self.assertEqual(p.stdout,'')
        self.assertFalse((self.root/'reports/samples-discovery.json').exists())

    def test_missing_required_digest_is_rejected(self):
        manifest=self.root/'vendor/superspear/checksums.json'
        manifest.write_text('{}')
        p=self.run_samples()
        self.assertNotEqual(p.returncode,0)
        self.assertIn('Invalid vendor checksum: engine.ts',p.stderr)
        self.assertFalse((self.root/'reports/samples-discovery.json').exists())

    def test_modified_helper_rejected_before_report_write(self):
        helper=self.root/'vendor/superspear/math-utils.ts'
        helper.write_text(helper.read_text()+'\n// accidental local drift\n')
        p=self.run_samples()
        self.assertNotEqual(p.returncode,0)
        self.assertIn('Vendor checksum mismatch: math-utils.ts',p.stderr)
        self.assertFalse((self.root/'reports/samples-discovery.json').exists())

if __name__=='__main__':unittest.main()
