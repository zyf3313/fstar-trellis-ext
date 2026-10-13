import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('personal', ROOT / 'scripts/personal.py')
personal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(personal)


class InstallBehaviorTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.project = self.base / 'consumer'
        self.project.mkdir()
        self.library = self.base / 'library'
        shutil.copytree(ROOT, self.library, ignore=shutil.ignore_patterns('__pycache__', 'node_modules', '.git', 'dist'))
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

    def test_multistack_and_database_are_selected_from_real_manifests(self):
        self.make('backend/pom.xml', '<project><modelVersion>4.0.0</modelVersion><parent><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-parent</artifactId><version>3.5.0</version></parent><properties><java.version>21</java.version></properties><dependencies><dependency><groupId>com.mysql</groupId><artifactId>mysql-connector-j</artifactId><version>9.0.0</version></dependency></dependencies></project>')
        self.make('web/package.json', json.dumps({'dependencies': {'vue': '3.5.0'}, 'devDependencies': {'typescript': '5.9.0'}}))
        result = personal.install(self.project)
        self.assertEqual(result['detected']['stacks'], ['java', 'javascript', 'maven', 'spring', 'typescript', 'vue'])
        self.assertIn('tools.database.usage', result['rules'])
        self.assertIn('engineering.frontend.interaction', result['rules'])
        self.assertFalse(any(rule.startswith('stacks.') for rule in result['rules']))
        self.assertNotIn('stacks.python', result['rules'])
        self.assertEqual(result['detected']['packages'][1]['versions']['vue'], '3.5.0')

    def test_no_database_and_ui_do_not_invent_vue_or_typescript(self):
        result = personal.install(self.project, capabilities=['ui'])
        self.assertIn('engineering.frontend.interaction', result['rules'])
        self.assertNotIn('stacks.vue', result['rules'])
        self.assertNotIn('stacks.typescript', result['rules'])
        self.assertNotIn('tools.database.usage', result['rules'])
        self.assertFalse((self.project / '.trellis/spec/guides/personal/tools/database/usage.md').exists())

    def test_declared_database_on_blank_project_enables_database_rules(self):
        result = personal.install(self.project, stacks=['python', 'sqlite'])
        self.assertIn('tools.database.usage', result['rules'])
        self.assertEqual(result['spec_sources_state'], 'project-spec-review-required')
        self.assertEqual(result['detected']['stack_state'], 'undetermined')

    def test_repeated_install_is_idempotent(self):
        first = personal.install(self.project)
        second = personal.install(self.project)
        self.assertEqual(second['status'], 'installed')
        self.assertTrue(all(row['action'] == 'reused' for row in second['actions']))
        self.assertEqual(self.project.joinpath('AGENTS.md').read_text().count('PERSONAL_TRELLIS:START'), 1)
        self.assertEqual(first['rules'], second['rules'])

    def test_review_required_stack_is_not_reported_as_source_or_catalog_failure(self):
        result = personal.install(self.project, stacks=['java', 'vue', 'sqlite', 'elixir'], offline=True)
        self.assertEqual(result['status'], 'installed')
        self.assertEqual(result['unmatched_stacks'], [])
        self.assertNotIn('unmatched_catalog_stacks', result)
        self.assertEqual(result['unrecognized_stacks'], ['elixir'])
        self.assertEqual(result['project_spec_review_stacks'], ['elixir', 'java', 'sqlite', 'vue'])
        self.assertEqual(result['spec_sources_state'], 'project-spec-review-required')

    def test_local_edits_are_preserved_and_candidate_is_rollback_owned(self):
        personal.install(self.project)
        target = self.make('.trellis/spec/guides/personal/core/context.md', '# Consumer-specific context\n')
        result = personal.install(self.project)
        self.assertEqual(result['status'], 'conflicts')
        conflict = next(row for row in result['actions'] if row['path'].endswith('core/context.md'))
        self.assertEqual(target.read_text(), '# Consumer-specific context\n')
        candidate = self.project / conflict['candidate']
        self.assertTrue(candidate.is_file())
        self.assertEqual(personal.rollback(self.project, result['revision'])['status'], 'rolled_back')
        self.assertFalse(candidate.exists())
        self.assertEqual(target.read_text(), '# Consumer-specific context\n')

    def test_upgrade_preserves_other_agents_text_and_user_block_changes(self):
        agents = self.make('AGENTS.md', '# Existing rules\nKeep local conventions.\n')
        personal.install(self.project)
        agents.write_text(agents.read_text() + '\nNew project instruction.\n')
        result = personal.install(self.project)
        self.assertEqual(result['status'], 'installed')
        self.assertIn('New project instruction.', agents.read_text())
        agents.write_text(agents.read_text().replace('## Personal workflow', '## My customized workflow'))
        expected = agents.read_bytes()
        result = personal.install(self.project)
        self.assertEqual(result['status'], 'conflicts')
        self.assertEqual(agents.read_bytes(), expected)

    def test_ambiguous_block_and_external_symlink_fail_before_mutation(self):
        self.make('AGENTS.md', '<!-- PERSONAL_TRELLIS:START -->\nunterminated')
        with self.assertRaises(ValueError):
            personal.install(self.project)
        self.assertFalse((self.project / '.trellis').exists())
        self.project.joinpath('AGENTS.md').unlink()
        outside = self.base / 'outside.md'
        outside.write_text('owned elsewhere')
        target = self.project / '.trellis/spec/guides/personal/core/context.md'
        target.parent.mkdir(parents=True)
        target.symlink_to(outside)
        with self.assertRaises(ValueError):
            personal.install(self.project)
        self.assertEqual(outside.read_text(), 'owned elsewhere')
        self.assertFalse((self.project / '.trellis/personal/install.json').exists())

    def test_existing_workflow_requires_explicit_adoption_and_can_restore(self):
        workflow = self.make('.trellis/workflow.md', '# Existing workflow\n')
        result = personal.install(self.project)
        self.assertEqual(result['status'], 'conflicts')
        self.assertEqual(workflow.read_text(), '# Existing workflow\n')
        adopted = personal.install(self.project, adopt_workflow=True)
        self.assertIn('Personal Chinese Design-First', workflow.read_text())
        self.assertEqual(personal.rollback(self.project, adopted['revision'])['status'], 'rolled_back')
        self.assertEqual(workflow.read_text(), '# Existing workflow\n')

    def test_interrupted_install_has_recoverable_journal(self):
        actual_write = personal.write
        def fail(path, content):
            if path == self.project / '.trellis/spec/guides/personal/core/authority.md':
                raise OSError('simulated interrupted write')
            actual_write(path, content)
        with patch.object(personal, 'write', side_effect=fail):
            with self.assertRaises(OSError):
                personal.install(self.project)
        backups = list((self.project / '.trellis/personal/backups').glob('*.json'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(personal.rollback(self.project, backups[0].stem)['status'], 'rolled_back')
        self.assertFalse((self.project / '.trellis/spec/guides/personal/core/context.md').exists())

    def test_rollback_preserves_edits_after_install(self):
        result = personal.install(self.project)
        target = self.make('.trellis/spec/guides/personal/core/context.md', '# Change after install\n')
        rolled = personal.rollback(self.project, result['revision'])
        self.assertEqual(rolled['status'], 'conflicts')
        self.assertEqual(target.read_text(), '# Change after install\n')

    def old_managed_stack(self, relative, content='# Old managed rule\n'):
        target = self.make(relative, content)
        state = self.project / '.trellis/personal/install.json'
        data = json.loads(state.read_text())
        data['files'][relative] = {'installed_sha256': personal.digest(target.read_bytes()), 'library_version': '1.0.0'}
        state.write_text(json.dumps(data))
        return target

    def test_retirement_removes_only_unchanged_owned_files_and_restores_backup(self):
        personal.install(self.project)
        paths = ['.trellis/spec/guides/personal/stacks/vue/index.md',
                 '.trellis/personal/library/specs/stacks/vue/index.md']
        owned = [self.old_managed_stack(path) for path in paths]
        edited = self.old_managed_stack('.trellis/spec/guides/personal/stacks/vue/edited.md')
        edited.write_text('# Project edit\n')
        added = self.make('.trellis/spec/guides/personal/stacks/vue/team.md', '# Added locally\n')
        result = personal.install(self.project, offline=True)
        self.assertEqual({a['path'] for a in result['actions'] if a['action'] == 'removed'}, set(paths))
        self.assertTrue(all(not path.exists() for path in owned))
        self.assertEqual(edited.read_text(), '# Project edit\n')
        self.assertEqual(added.read_text(), '# Added locally\n')
        self.assertEqual(result['status'], 'conflicts')
        self.assertFalse(any(a['action'] == 'removed' for a in personal.install(self.project)['actions']))
        self.assertEqual(personal.rollback(self.project, result['revision'])['status'], 'rolled_back')
        self.assertTrue(all(path.read_text() == '# Old managed rule\n' for path in owned))

    def test_retirement_rollback_preserves_recreated_file_and_is_repeatable(self):
        personal.install(self.project)
        relative = '.trellis/spec/guides/personal/stacks/python/index.md'
        target = self.old_managed_stack(relative)
        result = personal.install(self.project)
        self.assertFalse(target.exists())
        target.write_text('# Recreated after retirement\n')
        rolled = personal.rollback(self.project, result['revision'])
        self.assertIn(relative, rolled['conflicts'])
        self.assertEqual(target.read_text(), '# Recreated after retirement\n')
        target.unlink()
        self.assertEqual(personal.rollback(self.project, result['revision'])['status'], 'rolled_back')
        self.assertEqual(target.read_text(), '# Old managed rule\n')

    def test_default_install_never_fetches_or_generates_stack_rules(self):
        for stacks in ([], ['python', 'sqlite'], ['vue'], ['elixir']):
            with self.subTest(stacks=stacks), patch.object(personal.stack_sources, 'fetch', side_effect=AssertionError('unexpected fetch')):
                result = personal.install(self.project, stacks=stacks, offline=False)
                self.assertEqual(result['spec_sources_state'], 'project-spec-review-required')
                self.assertEqual(result['project_rules'], [])
                self.assertFalse((self.project / '.trellis/spec/guides/personal/stacks').exists())
                report = json.loads((self.project / '.trellis/personal/spec-sources.json').read_text())
                self.assertFalse(report['project_spec_complete'])
                self.assertFalse(report['adaptation_complete'])
                self.assertFalse((self.project / '.trellis/personal/library/specs/stacks').exists())

    def test_remembered_old_registry_cannot_reintroduce_withdrawn_profile(self):
        personal.install(self.project)
        receipt = next(row for row in json.loads((self.library / 'withdrawn-stack-sources.json').read_text())['sources']
                       if row['id'] == 'stacks.vue')
        target = self.old_managed_stack('.trellis/spec/guides/personal/stacks/vue/project-old.md')
        registry = self.make('old-registry/stack-sources.json', json.dumps({'schema_version': 1, 'profiles': [{
            'id': receipt['id'], 'stack': 'vue', 'kind': 'personal', 'major_versions': [3],
            'license': 'old candidate', 'coverage': ['withdrawn'],
            'source': {'path': 'missing-old-rule.md', 'sha256': receipt['sha256']}
        }]}))
        state_path = self.project / '.trellis/personal/install.json'
        state = json.loads(state_path.read_text())
        state.update({'stack_registry': str(registry), 'declared_stacks': ['vue'], 'stack_versions': {'vue': '3.5'}})
        state_path.write_text(json.dumps(state))
        with patch.object(personal.stack_sources, 'fetch', side_effect=AssertionError('withdrawn sources must not fetch')):
            result = personal.install(self.project)
        self.assertEqual(result['project_rules'], [])
        self.assertFalse(target.exists())
        report = json.loads((self.project / '.trellis/personal/spec-sources.json').read_text())
        self.assertIn(receipt['id'], report['withdrawn_profiles'])
        self.assertEqual(result['spec_sources_state'], 'project-spec-review-required')

    def test_optional_dependency_cycle_and_path_escape_are_rejected(self):
        data = json.loads((self.library / 'catalog.json').read_text())
        row = next(row for row in data['entries'] if row['id'] == 'tools.ui-design')
        row['depends_on'].append('tools.ui-design')
        (self.library / 'catalog.json').write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            personal.validate()
        row['depends_on'].remove('tools.ui-design')
        row['path'] = '../outside.md'
        (self.library / 'catalog.json').write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            personal.catalog()

    def test_design_changes_and_stale_outputs_fail(self):
        documents=[]
        for name in ['prd','tdd','ui']:
            path=self.make('docs/'+name+'.md', '# '+name+'\n')
            documents.append({'id':name,'path':str(path.relative_to(self.project)), 'version':'v1',
                              'approved_sha256':personal.digest(path.read_bytes())})
        artifact=self.make('design/screen.svg','<svg/>\n')
        manifest={'documents':documents,'features':[{'id':'F01','prd':'prd','tdd':'tdd','ui':'ui',
                  'acceptance':['AC01'],'artifacts':[{'path':'design/screen.svg','sha256':personal.digest(artifact.read_bytes()),
                  'source_document':'ui','source_sha256':documents[-1]['approved_sha256']}]}],
                  'confirmation':{'reference':'isolated test fixture, not real user acceptance'}}
        path=self.make('design-manifest.json',json.dumps(manifest))
        self.assertEqual(personal.verify_design(self.project,path.name)['status'],'passed')
        self.make('docs/ui.md','# Changed UI\n')
        result=personal.verify_design(self.project,path.name)
        self.assertEqual(result['status'],'failed')
        self.assertIn('unapproved or changed document: ui',result['failures'])
        self.make('docs/ui.md','# ui\n')
        artifact.write_text('<svg>changed</svg>\n')
        self.assertIn('stale artifact: design/screen.svg',personal.verify_design(self.project,path.name)['failures'])

    def test_preview_scaffold_is_portable_and_preserves_user_module_edits(self):
        self.make('pyproject.toml', '[project]\nname="fixture"\nrequires-python=">=3.10"\n')
        result = personal.install(self.project, capabilities=['ui'], preview_scaffold='design/preview')
        self.assertEqual(result['status'], 'installed')
        preview = self.project / 'design/preview'
        self.assertTrue((preview / 'package-lock.json').is_file())
        self.assertTrue((preview / 'public/design/exports/requirements.sketch').is_file())
        self.assertFalse((preview / 'node_modules').exists())
        self.assertFalse((preview / 'dist').exists())
        detected = personal.detect(self.project)
        self.assertEqual(detected['stacks'], ['python'])
        self.assertEqual(detected['preview_excluded_from_application_stack'], 'design/preview')
        target = preview / 'src/modules/requirements/RequirementsWorkspace.vue'
        target.write_text('<!-- Consumer-owned module -->\n')
        result = personal.install(self.project, capabilities=['ui'], preview_scaffold='design/preview')
        self.assertEqual(result['status'], 'conflicts')
        self.assertEqual(target.read_text(), '<!-- Consumer-owned module -->\n')
        self.assertEqual(personal.rollback(self.project, result['revision'])['status'], 'rolled_back')
        self.assertEqual(target.read_text(), '<!-- Consumer-owned module -->\n')


if __name__ == '__main__':
    unittest.main()
