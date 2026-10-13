import json
import os
from pathlib import Path
import sys
import signal
import subprocess
import time
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import tools
from mcp_stdio import MCPClient


class ProcessScopeTest(unittest.TestCase):
    def test_interrupted_helper_terminates_its_owned_child(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            marker = project / 'child.pid'
            child = 'import os,pathlib,time;pathlib.Path("child.pid").write_text(str(os.getpid()));time.sleep(30)'
            code = ('import sys,pathlib;sys.path.insert(0,sys.argv[1]);import tools;'
                    'tools.run(pathlib.Path(sys.argv[2]),[sys.executable,"-c",sys.argv[3]],"interrupt",timeout=40)')
            outer = subprocess.Popen([sys.executable,'-c',code,str(ROOT/'scripts'),str(project),child],
                                     stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                deadline = time.monotonic()+5
                while not marker.exists() and time.monotonic()<deadline:
                    time.sleep(.05)
                self.assertTrue(marker.exists(), 'Child never initialized')
                pid = int(marker.read_text())
                outer.send_signal(signal.SIGTERM)
                outer.communicate(timeout=5)
                self.assertNotEqual(outer.returncode, 0)
                with self.assertRaises(ProcessLookupError):
                    os.kill(pid, 0)
            finally:
                if outer.poll() is None:
                    outer.kill();outer.communicate(timeout=3)

    def test_interrupted_launcher_cannot_leave_a_grandchild_running(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            marker = project / 'heartbeat'
            grandchild = ('import signal,pathlib,time;signal.signal(signal.SIGTERM,lambda *_:None);'
                          '\nwhile True:pathlib.Path("heartbeat").write_text(str(time.time()));time.sleep(.05)')
            launcher = ('import subprocess,sys,time;subprocess.Popen([sys.executable,"-c",sys.argv[1]]);time.sleep(30)')
            code = ('import sys,pathlib;sys.path.insert(0,sys.argv[1]);import tools;'
                    'tools.run(pathlib.Path(sys.argv[2]),[sys.executable,"-c",sys.argv[3],sys.argv[4]],"launcher",timeout=40)')
            outer = subprocess.Popen([sys.executable,'-c',code,str(ROOT/'scripts'),str(project),launcher,grandchild],
                                     stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                deadline = time.monotonic()+5
                while not marker.exists() and time.monotonic()<deadline:time.sleep(.05)
                self.assertTrue(marker.exists(), 'Grandchild never initialized')
                outer.send_signal(signal.SIGTERM);outer.communicate(timeout=6)
                before = marker.read_text();time.sleep(.25)
                self.assertEqual(marker.read_text(), before, 'Grandchild survived helper interruption')
            finally:
                if outer.poll() is None:outer.kill();outer.communicate(timeout=3)

    def test_subprocess_pwd_cannot_write_to_inherited_parent(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory).resolve()
            project = parent / 'consumer'
            project.mkdir()
            command = [sys.executable, '-c',
                       'import os,pathlib; pathlib.Path(os.environ["PWD"],"marker").write_text("owned")']
            with patch.dict(os.environ, {'PWD': str(parent)}):
                tools.run(project, command, 'pwd-regression', timeout=10)
            self.assertTrue((project / 'marker').is_file())
            self.assertFalse((parent / 'marker').exists())

    def test_codex_environment_is_parseable_and_local_changes_are_preserved(self):
        try:
            import tomllib
        except ImportError:
            self.skipTest('Native TOML parsing requires the validation runtime Python 3.11+')
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            config = {'command': '/tools/qmd', 'args': ['mcp'],
                      'env': {'INDEX_PATH': str(project / '.qmd/index.sqlite')}}
            tools.merge_codex(project, {'personal_qmd': config})
            path = project / '.codex/config.toml'
            parsed = tomllib.loads(path.read_text())
            self.assertEqual(parsed['mcp_servers']['personal_qmd']['env'], config['env'])
            path.write_text(path.read_text().replace('/tools/qmd', '/my/custom/qmd'))
            before = path.read_bytes()
            result = tools.merge_codex(project, {'personal_qmd': config})
            self.assertEqual(result['status'], 'conflicts')
            self.assertEqual(path.read_bytes(), before)

    @unittest.skipUnless(os.environ.get('PERSONAL_TEST_QMD'), 'Set PERSONAL_TEST_QMD to the locked real binary')
    def test_actual_qmd_cli_and_mcp_use_child_index_and_preserve_parent(self):
        binary = str(Path(os.environ['PERSONAL_TEST_QMD']).resolve())
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory).resolve()
            project = parent / 'consumer'
            project.mkdir()
            tools.run(parent, [binary, 'init'], 'parent-init', env=tools.qmd_environment(parent), timeout=30)
            originals = {path: path.read_bytes() for path in (parent / '.qmd').iterdir() if path.is_file()}
            docs = project / 'docs'
            docs.mkdir()
            (docs / 'norm.md').write_text('# Child CodeGraph\n\n子项目唯一规则：先设计再开发。\n')
            with patch.dict(os.environ, {'PWD': str(parent), 'INDEX_PATH': str(parent / '.qmd/index.sqlite')}):
                env = tools.qmd_environment(project)
                tools.run(project, [binary, 'init'], 'child-init', env=env, timeout=30)
                tools.run(project, [binary, 'collection', 'add', str(docs), '--name', 'fixture-docs',
                                    '--mask', '**/*.md'], 'child-collection', env=env, timeout=30)
                output = tools.run(project, [binary, 'status'], 'child-status', env=env, timeout=30)
                self.assertIn(str(project / '.qmd/index.sqlite'), output)
                hits = json.loads(tools.run(project, [binary, 'search', 'CodeGraph', '--json'],
                                            'child-search', env=env, timeout=30))
                self.assertTrue(hits)
                with MCPClient([binary, 'mcp'], project, project / 'mcp.log', env=env, timeout=30) as client:
                    client.initialize(project)
                    client.call('status')
                    document = client.call('get', {'file': 'qmd://fixture-docs/norm.md'})
                    self.assertIn('子项目唯一规则', json.dumps(document, ensure_ascii=False))
            for path, content in originals.items():
                self.assertEqual(path.read_bytes(), content, 'Parent index changed: ' + str(path))


if __name__ == '__main__':
    unittest.main()
