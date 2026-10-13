"""Release tests exercise shipped output, tampering and filesystem boundaries."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('release', Path(__file__).resolve().parents[1] / 'scripts/release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'library'
        self.root.mkdir()
        (self.root / 'scripts').mkdir()
        (self.root / 'scripts/source.py').write_text('print("portable")\n')
        (self.root / 'library.json').write_text(json.dumps({'name': 'test', 'version': '1.0.0', 'publication': 'not_published', 'tested_trellis': '0.6.9', 'python': '>=3.9'}))
        (self.root / 'release-policy.json').write_text(json.dumps({'schema_version': 1, 'status': 'local_candidate', 'license_decision': 'pending', 'files': ['library.json', 'release-policy.json'], 'directories': ['scripts']}))

    def package(self, output='out'):
        result = release.build(self.root, self.base / output)
        return Path(result['archive'])

    def rewrite(self, archive, name, content):
        with zipfile.ZipFile(archive) as bundle:
            rows = [(item, bundle.read(item)) for item in bundle.infolist()]
        with zipfile.ZipFile(archive, 'w') as bundle:
            for item, body in rows:
                bundle.writestr(item, content if item.filename == name else body)

    def test_deterministic_across_mtime_and_output_directory(self):
        first = self.package('one').read_bytes()
        import os
        os.utime(self.root / 'scripts/source.py', (1000000000, 1000000000))
        second = self.package('two').read_bytes()
        self.assertEqual(first, second)

    def test_dependency_cache_env_and_unapproved_root_are_absent(self):
        for name in ['node_modules', '__pycache__', 'dist', '.tmp', 'private']:
            path = self.root / 'scripts' / name
            path.mkdir()
            (path / 'sensitive').write_text('DO NOT SHIP')
        (self.root / 'scripts/.env').write_text('TOKEN=secret')
        (self.root / 'unexpected.txt').write_text('PRIVATE')
        archive = self.package()
        with zipfile.ZipFile(archive) as bundle:
            self.assertFalse(any('DO NOT SHIP' in bundle.read(name).decode() for name in bundle.namelist()))
            self.assertFalse(any('unexpected' in name or '.env' in name for name in bundle.namelist()))
        self.assertEqual(release.verify(archive)['files'], 3)

    def test_source_symlink_is_rejected(self):
        (self.root / 'scripts/link').symlink_to(self.base / 'outside')
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            self.package()

    def test_runtime_candidate_file_is_rejected(self):
        (self.root / 'scripts/rule.md.new.012345').write_text('local candidate')
        with self.assertRaisesRegex(ValueError, 'candidate'):
            self.package()

    def test_content_tampering_is_detected(self):
        archive = self.package()
        self.rewrite(archive, 'personal-trellis-1.0.0/scripts/source.py', b'changed')
        with self.assertRaisesRegex(ValueError, 'integrity'):
            release.verify(archive)

    def test_unmanifested_file_is_rejected(self):
        archive = self.package()
        with zipfile.ZipFile(archive, 'a') as bundle:
            bundle.writestr('personal-trellis-1.0.0/scripts/extra.py', 'extra')
        with self.assertRaisesRegex(ValueError, 'integrity'):
            release.verify(archive)

    def test_traversal_and_symlink_archive_are_rejected(self):
        for name in ['../escape', '/absolute', 'personal-trellis-1.0.0/../escape']:
            archive = self.package()
            with zipfile.ZipFile(archive, 'a') as bundle:
                bundle.writestr(name, 'escape')
            with self.assertRaisesRegex(ValueError, 'Unsafe'):
                release.verify(archive)
        archive = self.package()
        with zipfile.ZipFile(archive, 'a') as bundle:
            item = zipfile.ZipInfo('personal-trellis-1.0.0/scripts/link')
            item.external_attr = 0o120777 << 16
            bundle.writestr(item, '/outside')
        with self.assertRaisesRegex(ValueError, 'non-regular'):
            release.verify(archive)

    def test_output_inside_source_and_missing_allowed_asset_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'outside'):
            release.build(self.root, self.root / 'scripts/output')
        (self.root / 'library.json').unlink()
        with self.assertRaisesRegex(ValueError, 'missing'):
            self.package()

    def repack(self, archive, mutate):
        with zipfile.ZipFile(archive) as bundle:
            bodies = {item.filename: bundle.read(item) for item in bundle.infolist()}
        prefix = 'personal-trellis-1.0.0/'
        manifest = json.loads(bodies.pop(prefix + release.MANIFEST))
        mutate(bodies, manifest, prefix)
        manifest['files'] = [{'path': name[len(prefix):], 'bytes': len(body), 'sha256': release.sha256(body)}
                             for name, body in sorted(bodies.items())]
        bodies[prefix + release.MANIFEST] = release.json_bytes(manifest)
        with zipfile.ZipFile(archive, 'w') as bundle:
            for name, body in bodies.items():
                bundle.writestr(name, body)

    def test_missing_declared_asset_is_rejected_even_with_consistent_manifest(self):
        archive = self.package()
        self.repack(archive, lambda bodies, manifest, prefix: bodies.pop(prefix + 'library.json'))
        with self.assertRaisesRegex(ValueError, 'Missing required'):
            release.verify(archive)

    def test_required_runtime_sources_cannot_be_omitted(self):
        rules = json.loads((self.root / 'release-policy.json').read_text())
        rules['directories'].append('examples')
        (self.root / 'release-policy.json').write_text(json.dumps(rules))
        for name in release.RUNTIME_SOURCES:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('source')
        archive = self.package()
        self.repack(archive, lambda bodies, manifest, prefix: bodies.pop(prefix + 'examples/ui-module/runtime/prototype.js'))
        with self.assertRaisesRegex(ValueError, 'Missing required'):
            release.verify(archive)
        (self.root / 'examples/ui-module/runtime/prototype.js').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing required'):
            self.package()

    def test_policy_license_and_schema_must_match_candidate_contract(self):
        for field, value in [('license_decision', 'unreviewed'), ('schema_version', 999), ('status', 'published')]:
            archive = self.package()
            def mutate(bodies, manifest, prefix):
                rules = json.loads(bodies[prefix + 'release-policy.json'])
                rules[field] = value
                bodies[prefix + 'release-policy.json'] = release.json_bytes(rules)
            self.repack(archive, mutate)
            with self.assertRaisesRegex(ValueError, 'Unsupported local-candidate'):
                release.verify(archive)

    def test_manifest_publication_and_version_must_match_library(self):
        for field, value in [('publication', 'published'), ('version', '9.9.9')]:
            archive = self.package()
            self.repack(archive, lambda bodies, manifest, prefix: manifest.update({field: value}))
            with self.assertRaisesRegex(ValueError, 'publication|metadata mismatch'):
                release.verify(archive)


if __name__ == '__main__':
    unittest.main()
