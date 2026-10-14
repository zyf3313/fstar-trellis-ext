"""Native layout and one-time retirement protection tests; no tool installation."""
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import subprocess
import sys
import unittest
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('retire', ROOT / 'scripts/retire-personal.py')
retire = importlib.util.module_from_spec(spec)
spec.loader.exec_module(retire)


class NativeLayoutTest(unittest.TestCase):
    def test_native_registry_and_removed_entries(self):
        entries = json.loads((ROOT / 'index.json').read_text())['templates']
        self.assertEqual([(e['id'], e['type'], e['path']) for e in entries], [('personal-core', 'spec', 'spec')])
        self.assertEqual(len(list((ROOT / 'spec/guides').glob('*.md'))), 3)
        for path in ['workflows', 'skills', 'specs', 'bundles', 'adapters', 'catalog.json', 'tools.lock.json',
                     'stack-definitions.json', 'scripts/personal.py', 'scripts/tools.py', 'scripts/ui_tools.py',
                     'scripts/database.py', 'scripts/mcp_stdio.py', 'scripts/stack_facts.py']:
            self.assertFalse((ROOT / path).exists(), path)
        self.assertEqual(len(list((ROOT / 'templates').rglob('*.md'))), 11)

    def test_metadata_and_selection(self):
        metadata = json.loads((ROOT / 'library.json').read_text())
        for key, expected in [('version', '1.0.0'), ('publication', 'not_published'),
                              ('visibility', 'private'), ('license_decision', 'pending')]:
            self.assertEqual(metadata[key], expected)
        selection = (ROOT / 'TOOL-SELECTION.zh-CN.md').read_text()
        self.assertEqual(selection.count('| 待定 |'), 7)

    def test_all_local_markdown_links(self):
        checked = 0
        for path in ROOT.rglob('*.md'):
            if any(part in {'node_modules', '.tmp', 'dist', '__pycache__'} for part in path.relative_to(ROOT).parts):
                continue
            for target in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)', path.read_text()):
                target = unquote(target.split('#')[0])
                if not target or '://' in target or target.startswith(('mailto:', 'data:')):
                    continue
                self.assertTrue((path.parent / target).exists(), f'{path.relative_to(ROOT)} -> {target}')
                checked += 1
        self.assertGreater(checked, 20)


class RetirementTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.candidate = self.root / 'native.md'
        self.candidate.write_bytes(b'# Native workflow\n')
        self.owned = '.trellis/spec/guides/personal/core/context.md'
        self.skill = '.agents/skills/personal-design/SKILL.md'
        self.block = retire.START + '\nowned personal rules\n' + retire.END
        self.put(self.owned, b'owned')
        self.put(self.skill, b'owned skill')
        self.put('AGENTS.md', ('local before\n' + self.block + '\nlocal after\n').encode())
        self.put('.trellis/workflow.md', b'old personal workflow')
        self.put('.trellis/.version', b'0.6.9')
        files = {p: {'installed_sha256': retire.digest(retire.read(self.root, p))} for p in
                 [self.owned, self.skill, '.trellis/workflow.md', 'AGENTS.md']}
        self.put(retire.STATE, retire.json_bytes({'files': files, 'agents_block_sha256': retire.digest(self.block.encode())}))

    def put(self, name, content):
        retire.write(self.root, name, content)

    def test_preview_no_mutation_and_apply_preserves_tools_and_local_files(self):
        unknown = '.trellis/spec/guides/personal/custom.md'
        self.put(unknown, b'local')
        self.put(self.skill, b'user edited skill')
        tools = ['.trellis/personal/library/scripts/tools.py', '.codex/config.toml',
                 '.agents/skills/impeccable/SKILL.md', '.trellis/config.yaml', '.trellis/spec/guides/index.md',
                 '.trellis/personal/tools/model.bin', '.trellis/.template-hashes.json']
        for path in tools:
            self.put(path, b'unchanged')
        before = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        plan = retire.plan(self.root, self.candidate, '0.6.9')
        self.assertEqual(before, {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        retire.execute(self.root, plan, apply=True)
        self.assertFalse((self.root / self.owned).exists())
        self.assertEqual(retire.read(self.root, self.skill), b'user edited skill')
        self.assertEqual(retire.read(self.root, unknown), b'local')
        self.assertEqual(retire.read(self.root, 'AGENTS.md'), b'local before\n\nlocal after\n')
        self.assertEqual(retire.read(self.root, '.trellis/workflow.md'), self.candidate.read_bytes())
        for path in tools:
            self.assertEqual(retire.read(self.root, path), b'unchanged')

    def test_native_candidate_version_and_modified_workflow_protection(self):
        candidate = self.root / 'native.md';candidate.write_bytes(b'# Native Trellis workflow\n')
        with self.assertRaisesRegex(ValueError, 'version'):
            retire.plan(self.root, candidate, '0.6.12')
        record = retire.plan(self.root, candidate, '0.6.9')
        retire.execute(self.root, record, apply=True)
        self.assertEqual(retire.read(self.root, '.trellis/workflow.md'), candidate.read_bytes())
        self.put('.trellis/workflow.md', b'user workflow')
        self.assertFalse(any(row['path'] == '.trellis/workflow.md' for row in retire.plan(self.root, candidate, '0.6.9')['changes']))

    def test_restore_and_refuse_overwrite_of_recreated_file(self):
        record = retire.plan(self.root, self.candidate, '0.6.9')
        retire.execute(self.root, record, apply=True)
        self.put(self.owned, b'recreated')
        actions = retire.execute(self.root, record, apply=True, restoring=True)
        self.assertEqual(retire.read(self.root, self.owned), b'recreated')
        self.assertTrue(any(row.get('reason') == 'changed_since_plan' for row in actions))
        self.assertEqual(retire.read(self.root, self.skill), b'owned skill')
        self.assertIn(self.block.encode(), retire.read(self.root, 'AGENTS.md'))

    def test_modified_block_and_symlinks_preserved(self):
        self.put('AGENTS.md', (self.block + '\n' + self.block).encode())
        (self.root / self.owned).unlink()
        (self.root / self.owned).symlink_to(self.root / self.skill)
        record = retire.plan(self.root, self.candidate, '0.6.9')
        self.assertFalse(any(row['path'] in [self.owned, 'AGENTS.md'] for row in record['changes']))
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            retire.read(self.root, '../outside')

    def test_cli_preview_apply_before_image_and_restore(self):
        def run(*args):
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/retire-personal.py'),
                                     '--project', str(self.root), '--native-workflow', str(self.candidate), '--native-version', '0.6.9', *args], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertEqual(run()['mode'], 'preview')
        self.assertFalse((self.root / retire.RECORDS).exists())
        applied = run('--apply')
        recovery = json.loads((self.root / applied['recovery']).read_text())
        self.assertEqual(recovery['status'], 'applied')
        owned = next(row for row in recovery['changes'] if row['path'] == self.owned)
        self.assertEqual(owned['before'], retire.encoded(b'owned'))
        self.assertFalse((self.root / self.owned).exists())
        run('--restore', applied['revision'])
        self.assertFalse((self.root / self.owned).exists())
        run('--restore', applied['revision'], '--apply')
        self.assertEqual(retire.read(self.root, self.owned), b'owned')

    def test_candidate_cannot_retain_retired_dependencies(self):
        for token in retire.REFERENCES:
            self.candidate.write_text('# Native candidate still referencing ' + token)
            with self.subTest(token=token), self.assertRaisesRegex(ValueError, 'candidate'):
                retire.plan(self.root, self.candidate, '0.6.9')

    def test_active_dependencies_block_all_changes(self):
        for mode in ('missing_candidate', 'edited_workflow', 'edited_block'):
            with self.subTest(mode=mode):
                workflow = retire.read(self.root, '.trellis/workflow.md')
                agents = retire.read(self.root, 'AGENTS.md')
                if mode == 'edited_workflow':
                    self.put('.trellis/workflow.md', b'edited workflow references personal-design')
                if mode == 'edited_block':
                    self.put('AGENTS.md', agents.replace(retire.START.encode(), (retire.START + ' edited').encode()))
                record = retire.plan(self.root) if mode == 'missing_candidate' else retire.plan(self.root, self.candidate, '0.6.9')
                self.assertTrue(record['blockers'])
                with self.assertRaisesRegex(ValueError, 'blocked'):
                    retire.execute(self.root, record, apply=True)
                self.assertEqual(retire.read(self.root, self.owned), b'owned')
                self.assertEqual(retire.read(self.root, self.skill), b'owned skill')
                self.put('.trellis/workflow.md', workflow)
                self.put('AGENTS.md', agents)

    def test_already_native_workflow_allows_retirement(self):
        self.put('.trellis/workflow.md', self.candidate.read_bytes())
        record = retire.plan(self.root)
        self.assertEqual(record['blockers'], [])
        retire.execute(self.root, record, apply=True)
        self.assertFalse((self.root / self.skill).exists())

    def test_missing_ownership_is_refused(self):
        (self.root / retire.STATE).unlink()
        with self.assertRaisesRegex(ValueError, 'ownership'):
            retire.plan(self.root, self.candidate, '0.6.9')


if __name__ == '__main__':
    unittest.main()
