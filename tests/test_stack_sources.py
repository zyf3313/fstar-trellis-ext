import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('source_personal', ROOT / 'scripts/personal.py')
personal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(personal)
sources = personal.stack_sources


class StackSourceTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.project = self.base / 'consumer'
        self.project.mkdir()
        self.library = self.base / 'library'
        shutil.copytree(ROOT, self.library, ignore=shutil.ignore_patterns('node_modules', 'dist', '__pycache__', '.git'))
        self.library_patch = patch.object(personal, 'LIBRARY', self.library)
        self.library_patch.start()

    def tearDown(self):
        self.library_patch.stop()
        self.temp.cleanup()

    def make(self, relative, body):
        path = self.project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
        return path

    def vue(self, scope='web', version='3.5.0'):
        self.make(scope + '/package.json', json.dumps({'dependencies': {'vue': version}, 'scripts': {'typecheck': 'vue-tsc', 'build': 'vite build'}}))

    def local_registry(self, stack='vue', major=3, body='# Personal convention\nUse the existing component library.\n'):
        folder = self.base / 'registry'
        folder.mkdir(exist_ok=True)
        raw = body.encode()
        (folder / 'rules.md').write_bytes(raw)
        profile = {'id': 'personal.' + stack + '.team', 'kind': 'personal', 'stack': stack,
                   'major_versions': [major], 'license': 'fixture', 'coverage': ['team component boundary'],
                   'source': {'path': 'rules.md', 'sha256': personal.digest(raw)}}
        path = folder / 'stack-sources.json'
        path.write_text(json.dumps({'schema_version': 1, 'profiles': [profile]}))
        return path, profile

    def official_go(self):
        raw = b'# Official Go reference\nGo source conventions.\n'
        path = self.library / 'stack-sources.json'
        data = json.loads(path.read_text())
        row = next(row for row in data['profiles'] if row['stack'] == 'go')
        row['source']['sha256'] = personal.digest(raw)
        path.write_text(json.dumps(data))
        self.make('service/go.mod', 'module fixture\n\ngo 1.24.0\n')
        return raw

    def test_personal_registry_precedes_bundled_and_adapts_real_package(self):
        self.vue()
        path, profile = self.local_registry()
        result = personal.install(self.project, stack_registry=str(path), offline=True)
        report = json.loads((self.project / '.trellis/personal/spec-sources.json').read_text())
        row = next(row for row in report['packages'] if row['stack'] == 'vue')
        self.assertEqual(row['profile_id'], profile['id'])
        self.assertEqual(row['source']['sha256'], profile['source']['sha256'])
        self.assertEqual(row['manifest'], 'web/package.json')
        text = (self.project / row['target']).read_text()
        self.assertIn('existing component library', text)
        self.assertIn('npm run typecheck', text)
        self.assertFalse(report['adaptation_complete'])
        self.assertEqual(result['spec_sources_state'], 'acquired')

    def test_incompatible_personal_profile_falls_back_without_applying_its_rules(self):
        self.vue()
        path, _ = self.local_registry(major=2, body='# Vue 2 legacy-only rule\n')
        report, assets, _ = personal.query_stacks(self.project, registry=str(path), offline=True)
        row = next(row for row in report['packages'] if row['stack'] == 'vue')
        self.assertEqual(row['profile_id'], 'stacks.vue')
        self.assertEqual(row['attempts'][0]['state'], 'version_mismatch')
        self.assertNotIn(b'legacy-only', assets[row['target']])

    def test_official_fallback_fetches_once_and_reuses_verified_cache_offline(self):
        raw = self.official_go()
        with patch.object(sources, 'fetch', return_value=raw) as request:
            report, assets, _ = personal.query_stacks(self.project)
        row = report['packages'][0]
        self.assertEqual(request.call_count, 1)
        self.assertEqual(row['kind'], 'official')
        self.assertEqual(row['source']['transport'], 'https_verified')
        self.assertIn(b'Goroutines'.lower(), assets[row['target']].lower())
        with patch.object(sources, 'fetch', side_effect=AssertionError('offline must not fetch')):
            repeat, _, _ = personal.query_stacks(self.project, offline=True)
        self.assertTrue(repeat['acquisition_complete'])
        self.assertEqual(repeat['packages'][0]['source']['transport'], 'verified_cache')

    def test_offline_without_cache_preserves_explicit_gap(self):
        self.official_go()
        with patch.object(sources, 'fetch', side_effect=AssertionError('offline must not fetch')):
            report, _, _ = personal.query_stacks(self.project, offline=True)
        self.assertFalse(report['acquisition_complete'])
        self.assertEqual(report['packages'][0]['status'], 'acquisition_failed')
        self.assertIn('offline_cache_miss', report['packages'][0]['attempts'][0]['reason'])

    def test_modified_reference_and_wrong_download_hash_are_rejected(self):
        raw = self.official_go()
        with patch.object(sources, 'fetch', return_value=b'wrong data'):
            report, _, _ = personal.query_stacks(self.project)
        self.assertFalse(report['acquisition_complete'])
        with patch.object(sources, 'fetch', return_value=raw):
            report, _, _ = personal.query_stacks(self.project)
        cache = self.project / report['packages'][0]['source']['cache_path']
        cache.write_text('locally modified')
        with patch.object(sources, 'fetch', side_effect=AssertionError('must preserve modified cache')):
            report, _, _ = personal.query_stacks(self.project, offline=True)
        self.assertIn('Cached source was modified', report['packages'][0]['attempts'][0]['reason'])

    def test_unknown_stack_and_blank_project_do_not_invent_rules_or_commands(self):
        report, assets, _ = personal.query_stacks(self.project, ['elixir'], offline=True)
        row = report['packages'][0]
        self.assertEqual(row['status'], 'missing_source')
        self.assertIsNone(row['manifest'])
        self.assertEqual(row['commands'], [])
        self.assertIn('official coding conventions', row['research_query'])
        self.assertNotIn(b'passed', assets[row['target']])
        empty, _, _ = personal.query_stacks(self.project, offline=True)
        self.assertEqual(empty['state'], 'stack_undetermined')

    def test_vue_two_cannot_install_vue_three_baseline(self):
        self.vue(version='2.7.16')
        result = personal.install(self.project, offline=True)
        report = json.loads((self.project / '.trellis/personal/spec-sources.json').read_text())
        row = next(row for row in report['packages'] if row['stack'] == 'vue')
        self.assertEqual(row['status'], 'acquired')
        self.assertEqual(row['profile_id'], 'stacks.vue.legacy-v2')
        self.assertEqual(result['spec_sources_state'], 'acquired')
        self.assertIn('stacks.vue.legacy-v2', result['rules'])
        self.assertNotIn('stacks.vue', result['rules'])
        self.assertFalse((self.project / '.trellis/spec/guides/personal/stacks/vue/index.md').exists())

    def test_multistack_version_scopes_stay_distinct(self):
        self.vue('legacy', '2.7.16')
        self.vue('modern', '3.5.0')
        report, assets, entries = personal.query_stacks(self.project, offline=True)
        vue_rows = [row for row in report['packages'] if row['stack'] == 'vue']
        self.assertEqual(len({row['target'] for row in vue_rows}), 2)
        self.assertEqual({row['scope']: row['status'] for row in vue_rows}, {'legacy': 'acquired', 'modern': 'acquired'})
        self.assertEqual(len({entry['id'] for entry in entries}), len(entries))

    def test_lock_version_and_configured_commands_are_evidence_without_execution(self):
        self.vue(version='>=2')
        self.make('web/package-lock.json', json.dumps({'packages': {'node_modules/vue': {'version': '3.5.43'}}}))
        found = personal.detect(self.project)['packages'][0]
        self.assertEqual(found['versions']['vue'], '3.5.43')
        self.assertIn('resolved dependency', found['version_evidence']['vue'])
        self.assertEqual(found['commands'], ['npm run typecheck', 'npm run build'])

    def test_python_maven_go_rust_versions_and_database_driver_boundary(self):
        self.make('api/pom.xml', '<project><parent><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-parent</artifactId><version>3.5.0</version></parent><properties><java.version>21</java.version></properties><dependencies><dependency><groupId>com.mysql</groupId><artifactId>mysql-connector-j</artifactId><version>9.0.0</version></dependency></dependencies></project>')
        self.make('worker/pyproject.toml', '[project]\nrequires-python=">=3.10,<4"\n[tool.pytest.ini_options]\n')
        self.make('worker/requirements.txt', 'psycopg==3.2.0\n')
        self.make('worker/.python-version', '3.12.0\n')
        self.make('service/go.mod', 'module fixture\ngo 1.24.0\n')
        self.make('native/Cargo.toml', '[package]\nrust-version="1.85"\n')
        found = personal.detect(self.project)
        by_path = {row['path']: row for row in found['packages']}
        self.assertEqual(by_path['api/pom.xml']['versions'], {'java': '21', 'spring': '3.5.0'})
        self.assertEqual(by_path['worker/pyproject.toml']['versions']['python'], '3.12.0')
        self.assertEqual(by_path['native/Cargo.toml']['versions']['rust'], '1.85')
        self.assertEqual(found['databases'], ['mysql', 'postgres'])
        self.assertNotIn('mysql', by_path['api/pom.xml']['versions'])
        report, _, _ = personal.query_stacks(self.project, offline=True)
        python_rows = [row for row in report['packages'] if row['stack'] == 'python']
        self.assertEqual(len(python_rows), 1)
        self.assertEqual(len(python_rows[0]['manifests']), 2)

    def test_declared_version_does_not_override_actual_resolved_version(self):
        self.vue(version='3.5.43')
        report, _, _ = personal.query_stacks(self.project, versions={'vue': '3.6.0'}, offline=True)
        row = next(row for row in report['packages'] if row['stack'] == 'vue')
        self.assertEqual(row['version'], '3.5.43')
        self.assertEqual(row['status'], 'declaration_conflict')

    def test_compatible_python_declaration_narrows_unbounded_constraint(self):
        self.make('pyproject.toml', '[project]\nrequires-python=">=3.10"\n')
        report, _, _ = personal.query_stacks(self.project, versions={'python': '3.12.0'}, offline=True)
        self.assertEqual(report['packages'][0]['version'], '3.12.0')
        self.assertEqual(report['packages'][0]['status'], 'acquired')
        bad, _, _ = personal.query_stacks(self.project, versions={'python': '3.9.0'}, offline=True)
        self.assertEqual(bad['packages'][0]['status'], 'declaration_conflict')

    def test_major_constraints_are_conservative(self):
        for text, expected in [('^3.5.43', {3}), ('>=3.10,<4', {3}), ('>=3.10,<4.2', {3, 4}),
                               ('>=3.10', None), ('workspace:*', None), ('^2 || ^3', {2, 3})]:
            self.assertEqual(personal.stack_facts.major_set(text), expected)

    def test_remote_registry_requires_immutable_commit_and_preserves_subdirectory(self):
        with self.assertRaises(ValueError):
            sources.registry_locator('gh:team/rules#main')
        base, ref = sources.registry_locator('gh:team/rules/personal#' + 'a' * 40)
        self.assertTrue(base.endswith('/' + ref + '/personal/'))
        path, profile = self.local_registry()
        self.vue()
        raw = path.read_bytes()
        content = path.parent.joinpath('rules.md').read_bytes()
        locator = 'gh:team/rules/personal#' + 'a' * 40
        def request(url, *args):
            return raw if url.endswith('stack-sources.json') else content
        with patch.object(sources, 'fetch', side_effect=request) as fetch:
            report, _, _ = personal.query_stacks(self.project, registry=locator)
        self.assertEqual(fetch.call_count, 2)
        self.assertEqual(report['registry']['ref'], 'a' * 40)
        row = next(row for row in report['packages'] if row['stack'] == 'vue')
        self.assertIn('/personal/rules.md', row['source']['url'])
        with patch.object(sources, 'fetch', side_effect=AssertionError('no network')):
            cached, _, _ = personal.query_stacks(self.project, registry=locator, offline=True)
        self.assertTrue(cached['acquisition_complete'])

    def test_missing_remote_registry_can_continue_with_local_rules_but_is_incomplete(self):
        self.vue()
        report, _, _ = personal.query_stacks(self.project, registry='gh:team/rules#' + 'b' * 40, offline=True)
        self.assertFalse(report['acquisition_complete'])
        self.assertEqual(report['packages'][1]['profile_id'], 'stacks.vue')
        self.assertIn('offline_registry_cache_miss', report['registry_errors'])

    def test_bad_paths_credentials_and_schema_fail_before_asset_install(self):
        path, profile = self.local_registry()
        profile['source']['path'] = '../outside.md'
        path.write_text(json.dumps({'schema_version': 1, 'profiles': [profile]}))
        with self.assertRaises(ValueError):
            personal.install(self.project, ['vue'], stack_versions={'vue': '3'}, stack_registry=str(path), offline=True)
        self.assertFalse((self.project / '.trellis/spec').exists())
        for url in ['http://example.com/rules', 'https://user:secret@example.com/rules', 'https://example.com/rules?token=secret']:
            with self.assertRaises(ValueError):
                sources.https_url(url)
        with self.assertRaises(ValueError):
            sources.validate_registry({'schema_version': 2, 'profiles': []})

    def test_budget_and_timeout_return_gaps(self):
        self.official_go()
        io = type('IO', (), {'safe': staticmethod(personal.safe), 'write': staticmethod(personal.write)})
        with patch.object(sources, 'fetch', side_effect=AssertionError('deadline exhausted')):
            report, _, _ = sources.resolve(self.project, self.library, personal.catalog(), personal.detect(self.project),
                                           ['go'], {}, None, False, io, budget=0)
        self.assertIn('source_budget_exhausted', report['packages'][0]['attempts'][0]['reason'])
        with patch.object(sources.subprocess, 'run', side_effect=subprocess.TimeoutExpired('fetch', 20)):
            with self.assertRaisesRegex(OSError, 'source_download_timeout'):
                sources.fetch('https://example.com/reference')

    def test_local_adaptation_edits_are_protected_and_source_update_is_rollback_owned(self):
        self.vue()
        path, profile = self.local_registry()
        personal.install(self.project, stack_registry=str(path), offline=True)
        report = json.loads((self.project / '.trellis/personal/spec-sources.json').read_text())
        target = next(row['target'] for row in report['packages'] if row['stack'] == 'vue')
        adapted = self.make(target, '# Consumer-owned adaptation\n')
        result = personal.install(self.project, offline=True)
        self.assertEqual(result['status'], 'conflicts')
        conflict = next(row for row in result['actions'] if row['path'] == target)
        self.assertTrue((self.project / conflict['candidate']).is_file())
        self.assertEqual(personal.rollback(self.project, result['revision'])['status'], 'rolled_back')
        self.assertEqual(adapted.read_text(), '# Consumer-owned adaptation\n')

    def test_category_indexes_link_only_selected_rules_and_project_scopes(self):
        self.vue()
        result = personal.install(self.project, offline=True)
        root = self.project / '.trellis/spec/guides/personal'
        self.assertTrue((root / 'stacks/index.md').is_file())
        body = (root / 'stacks/index.md').read_text()
        self.assertIn('vue/index.md', body)
        self.assertIn('project-', body)
        self.assertNotIn('python/index.md', body)
        self.assertIn('## Quality Check', body)

    def test_blank_project_declarations_survive_repeated_initialization(self):
        personal.install(self.project, ['python', 'sqlite'], ['ui'], stack_versions={'python': '3.12.0'}, offline=True)
        again = personal.install(self.project, offline=True)
        self.assertEqual(again['selected_stacks'], ['python', 'sqlite'])
        self.assertIn('ui', again['selected_capabilities'])
        self.assertIn('database', again['selected_capabilities'])
        report, _, _ = personal.query_stacks(self.project, offline=True)
        self.assertEqual({row['stack'] for row in report['packages']}, {'python', 'sqlite'})

    def test_reference_content_is_not_promoted_to_executable_project_rules(self):
        raw = b'# Reference sample\nRun an unrelated destructive script.\n'
        self.official_go()
        p = self.library / 'stack-sources.json'
        data = json.loads(p.read_text())
        next(row for row in data['profiles'] if row['stack'] == 'go')['source']['sha256'] = personal.digest(raw)
        p.write_text(json.dumps(data))
        with patch.object(sources, 'fetch', return_value=raw):
            report, assets, _ = personal.query_stacks(self.project)
        row = report['packages'][0]
        self.assertEqual(row['reference_state'], 'downloaded_reference_not_executable')
        self.assertNotIn(b'unrelated destructive script', assets[row['target']])

    def test_opensource_profile_can_fill_failed_official_acquisition(self):
        self.official_go()
        path, profile = self.local_registry(stack='go', major=1)
        profile['kind'] = 'opensource'
        profile['adaptation'] = 'specs/stacks/go/adaptation.md'
        path.write_text(json.dumps({'schema_version': 1, 'profiles': [profile]}))
        report, _, _ = personal.query_stacks(self.project, registry=str(path), offline=True)
        self.assertEqual(report['packages'][0]['kind'], 'opensource')
        self.assertEqual(report['packages'][0]['attempts'][0]['state'], 'acquisition_failed')
        self.assertTrue(report['acquisition_complete'])

    def test_malformed_profile_and_dependency_types_are_explicit_errors(self):
        path, profile = self.local_registry()
        profile['version_independent'] = 'false'
        path.write_text(json.dumps({'schema_version': 1, 'profiles': [profile]}))
        with self.assertRaisesRegex(ValueError, 'boolean'):
            personal.query_stacks(self.project, registry=str(path), offline=True)
        self.make('package.json', json.dumps({'dependencies': {'vue': {'version': '3'}}}))
        with self.assertRaisesRegex(ValueError, 'must be strings'):
            personal.detect(self.project)
        self.assertFalse((self.project / '.trellis/spec').exists())

    def test_failed_source_repair_preserves_last_acquired_rule(self):
        raw = self.official_go()
        with patch.object(sources, 'fetch', return_value=raw):
            personal.install(self.project)
        previous = json.loads((self.project / '.trellis/personal/spec-sources.json').read_text())
        row = previous['packages'][0]
        target = self.project / row['target']
        before = target.read_bytes()
        (self.project / row['source']['cache_path']).unlink()
        result = personal.install(self.project, offline=True)
        self.assertEqual(target.read_bytes(), before)
        self.assertEqual(result['status'], 'conflicts')
        conflict = next(action for action in result['actions'] if action['path'] == row['target'])
        self.assertTrue((self.project / conflict['candidate']).exists())
        again = personal.install(self.project, offline=True)
        self.assertEqual(again['status'], 'conflicts')
        self.assertEqual(target.read_bytes(), before)

    def test_failed_preferred_source_does_not_silently_downgrade_to_generic_rule(self):
        self.vue()
        path, _ = self.local_registry(body='# Team architecture\nKeep the existing explicit module boundary.\n')
        personal.install(self.project, stack_registry=str(path), offline=True)
        previous = json.loads((self.project / '.trellis/personal/spec-sources.json').read_text())
        row = next(row for row in previous['packages'] if row['stack'] == 'vue')
        target = self.project / row['target']
        before = target.read_bytes()
        (path.parent / 'rules.md').write_text('# Changed without updated digest\n')
        result = personal.install(self.project, offline=True)
        self.assertEqual(target.read_bytes(), before)
        self.assertEqual(result['status'], 'conflicts')
        current = json.loads((self.project / '.trellis/personal/spec-sources.json').read_text())
        updated = next(row for row in current['packages'] if row['stack'] == 'vue')
        self.assertEqual(updated['adoption_state'], 'preserved_previous_rule')
        self.assertTrue((self.project / updated['candidate']).is_file())
        again = personal.install(self.project, offline=True)
        self.assertEqual(again['status'], 'conflicts')
        self.assertEqual(target.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
