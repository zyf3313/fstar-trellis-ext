import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import tools
import ui_tools


class UISkillInstallationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.project = self.root / 'project'
        self.source = self.root / 'source'
        self.project.mkdir()
        self.source.mkdir()
        (self.source / 'SKILL.md').write_text('---\nname: impeccable\n---\nDesign example.\n')
        (self.source / 'reference.md').write_text('Existing guide.\n')
        self.row = {'version': 'fixture-1', 'source_ref': 'a' * 40}

    def install(self):
        return ui_tools.install_tree(self.project, 'impeccable', self.source, self.row)

    def test_reuse_does_not_rewrite_existing_files(self):
        self.assertEqual(self.install()['installation'], 'installed')
        path = self.project / '.agents/skills/impeccable/reference.md'
        previous = path.stat().st_mtime_ns
        self.assertEqual(self.install()['installation'], 'reused')
        self.assertEqual(path.stat().st_mtime_ns, previous)

    def test_local_change_blocks_whole_upgrade_and_keeps_extra_file(self):
        self.install()
        target = self.project / '.agents/skills/impeccable'
        (target / 'reference.md').write_text('My local rule.\n')
        (target / 'own.md').write_text('My extra rule.\n')
        before = (target / 'SKILL.md').read_bytes()
        (self.source / 'SKILL.md').write_text('New upstream skill.\n')
        result = self.install()
        self.assertEqual(result['status'], 'conflicts')
        self.assertEqual((target / 'SKILL.md').read_bytes(), before)
        self.assertEqual((target / 'reference.md').read_text(), 'My local rule.\n')
        self.assertEqual((target / 'own.md').read_text(), 'My extra rule.\n')
        self.assertTrue((self.project / result['candidate'] / 'SKILL.md').is_file())

    def test_upgrade_removes_only_unchanged_owned_obsolete_files(self):
        self.install()
        target = self.project / '.agents/skills/impeccable'
        (target / 'own.md').write_text('Keep me.\n')
        (self.source / 'reference.md').unlink()
        (self.source / 'new.md').write_text('New guide.\n')
        result = self.install()
        self.assertEqual(result['installation'], 'updated')
        self.assertFalse((target / 'reference.md').exists())
        self.assertEqual((target / 'own.md').read_text(), 'Keep me.\n')
        self.assertEqual((target / 'new.md').read_text(), 'New guide.\n')

    def test_source_and_destination_links_are_rejected_before_writes(self):
        outside = self.root / 'private.txt'
        outside.write_text('Private.\n')
        (self.source / 'linked.md').symlink_to(outside)
        with self.assertRaises(ValueError):
            self.install()
        self.assertFalse((self.project / '.agents').exists())
        (self.source / 'linked.md').unlink()
        redirected = self.project / 'other-owned-directory'
        redirected.mkdir()
        target = self.project / '.agents/skills/impeccable'
        target.parent.mkdir(parents=True)
        target.symlink_to(redirected, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.install()
        self.assertTrue(target.is_symlink())
        self.assertEqual(list(redirected.iterdir()), [])

    def test_failure_between_renames_restores_entire_previous_tree(self):
        self.install()
        target = self.project / '.agents/skills/impeccable'
        before = ui_tools.inventory(target)
        (self.source / 'reference.md').write_text('Updated guide.\n')
        actual_replace = ui_tools.os.replace
        def fail_swap(source, destination):
            if Path(destination) == target and Path(source).parent == target.parent:
                raise OSError('Simulated swap failure')
            return actual_replace(source, destination)
        with patch.object(ui_tools.os, 'replace', side_effect=fail_swap):
            with self.assertRaises(OSError):
                self.install()
        self.assertEqual(ui_tools.inventory(target), before)

    def test_journal_written_before_first_rename_preserves_original_target(self):
        self.install()
        target = self.project / '.agents/skills/impeccable'
        state = self.project / '.trellis/personal/ui-tools/impeccable.json'
        journal = self.project / '.trellis/personal/ui-tools/impeccable-transaction.json'
        before = ui_tools.inventory(target)
        journal.write_text(json.dumps({'transaction': 'interrupted-new', 'target_moved': True,
                                      'backup': '.trellis/personal/ui-tools/backups/impeccable-fixture',
                                      'old_state': json.loads(state.read_text())}))
        ui_tools.restore_interrupted(self.project, 'impeccable')
        self.assertEqual(ui_tools.inventory(target), before)
        self.assertFalse(journal.exists())

    def test_conditional_initialization_uses_real_or_declared_ui(self):
        (self.project / 'pyproject.toml').write_text('[project]\nname="service"\n')
        self.assertFalse(tools.ui_tools_required(self.project))
        self.assertTrue(tools.ui_tools_required(self.project, True))
        (self.project / 'package.json').write_text(json.dumps({'dependencies': {'vue': '3.5.43'}}))
        self.assertTrue(tools.ui_tools_required(self.project))

    def test_default_ui_profile_selects_both_providers_without_other_frameworks(self):
        with patch.object(sys, 'argv', ['tools.py', '--project', str(self.project), '--ui']), \
             patch.object(tools, 'initialize', return_value={'tools': {}}) as initialize:
            self.assertEqual(tools.main(), 0)
        self.assertEqual(initialize.call_args.args[1], ['codegraph','rtk','qmd','impeccable','ui-ux-pro-max'])

    def test_unsafe_archive_is_rejected_without_extracting_selected_files(self):
        archive = self.root / 'source.zip'
        with zipfile.ZipFile(archive, 'w') as content:
            content.writestr('upstream/LICENSE', 'License')
            content.writestr('upstream/.agents/skills/impeccable/SKILL.md', 'Skill')
            content.writestr('upstream/.agents/skills/impeccable/../../../escaped.txt', 'Bad')
        destination = self.root / 'extract'
        destination.mkdir()
        with self.assertRaises(ValueError):
            ui_tools.extract_skill_archive(archive, destination, '.agents/skills/impeccable')
        self.assertEqual(list(destination.iterdir()), [])

    def test_command_failure_preserves_provider_exit_code(self):
        with patch.object(sys, 'argv', ['ui_tools.py','--project',str(self.project),'--tool','ui-ux-pro-max','form']), \
             patch.object(ui_tools, 'run', side_effect=tools.ToolCommandError(2, 'Findings available')):
            self.assertEqual(ui_tools.main(), 2)


if __name__ == '__main__':
    unittest.main()
