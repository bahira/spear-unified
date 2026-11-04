"""Incomplete manifests must fail before any Node subprocess can be launched."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from spear import discovery

ROOT=Path(__file__).resolve().parents[1]

class DiscoveryManifestChecks(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='spear-discovery-manifest-')
        self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)
        shutil.copytree(ROOT/'vendor/superspear',self.root/'vendor/superspear')
        self.manifest=self.root/'vendor/superspear/checksums.json'
        self.original=json.loads(self.manifest.read_text())

    def assert_rejected_without_launch(self,manifest,message):
        self.manifest.write_text(json.dumps(manifest))
        with patch('spear.discovery.ROOT',self.root), patch('spear.discovery.subprocess.run') as run:
            # Sentinel makes a regression obvious and avoids executing altered files.
            run.side_effect=AssertionError('Unverified Node subprocess was launched')
            with self.assertRaisesRegex(ValueError,message):
                discovery.discover({'formula':'x*x'})
            run.assert_not_called()

    def test_empty_manifest_cannot_bypass_integrity_checks(self):
        engine=self.root/'vendor/superspear/engine.ts'
        engine.write_text(engine.read_text()+'\n// local drift\n')
        self.assert_rejected_without_launch({},'Invalid vendor checksum: engine.ts')

    def test_omitted_helper_digest_cannot_hide_modified_helper(self):
        helper=self.root/'vendor/superspear/math-utils.ts'
        helper.write_text(helper.read_text()+'\n// local drift\n')
        manifest=dict(self.original)
        del manifest['math-utils.ts']
        self.assert_rejected_without_launch(manifest,'Invalid vendor checksum: math-utils.ts')

    def test_manifest_must_be_an_object(self):
        for manifest in (None,[],42):
            with self.subTest(manifest=manifest):
                self.assert_rejected_without_launch(manifest,'Invalid vendor checksum manifest')

    def test_required_digest_must_be_sha256_hex(self):
        for value in (None,42,'','a'*63,'z'*64):
            with self.subTest(value=value):
                manifest={**self.original,'engine.ts':value}
                self.assert_rejected_without_launch(manifest,'Invalid vendor checksum: engine.ts')
