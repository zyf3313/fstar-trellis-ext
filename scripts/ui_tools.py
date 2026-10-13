#!/usr/bin/env python3
"""Install and probe scoped UI skills without replacing local edits or hooks."""
import argparse
import json
import os
from pathlib import Path
import platform
import re
import shutil
import sys
import tempfile
import zipfile

from personal import LIBRARY, digest, json_bytes, load, safe, stamp, write
from tools import ToolCommandError, npm_tool, run

NAMES = ('impeccable', 'ui-ux-pro-max')


def atomic_record(path, value):
    temporary = path.with_name('.' + path.name + '-' + stamp())
    write(temporary, json_bytes(value))
    os.replace(temporary, path)


def skill_target(project, name):
    raw_target = project / '.agents/skills' / name
    if any(path.is_symlink() for path in [raw_target, *raw_target.parents] if path != project):
        raise ValueError('Skill installation path contains a symlink')
    return safe(project, '.agents/skills/' + name)


def inventory(directory):
    """Validate the entire input tree before any destination mutation."""
    if Path(directory).is_symlink():
        raise ValueError('Skill source root is a symlink')
    root = Path(directory).resolve()
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('Skill symlinks require explicit adaptation: ' + str(path))
        if path.is_file():
            result[path.relative_to(root).as_posix()] = digest(path.read_bytes())
    if 'SKILL.md' not in result:
        raise ValueError('Provider did not produce SKILL.md')
    return result


def restore_interrupted(project, name):
    journal = safe(project, '.trellis/personal/ui-tools/' + name + '-transaction.json')
    if not journal.exists():
        return
    saved = load(journal)
    target = skill_target(project, name)
    backup = safe(project, saved['backup'])
    if backup.parent != safe(project, '.trellis/personal/ui-tools/backups') or not backup.name.startswith(name + '-'):
        raise ValueError('Invalid UI skill recovery backup')
    state = safe(project, '.trellis/personal/ui-tools/' + name + '.json')
    current = load(state) if state.exists() else {}
    # A committed manifest identifies the swapped tree. Otherwise restore the
    # saved before-image, including an interruption between the two renames.
    if current.get('transaction') != saved['transaction']:
        if backup.exists():
            if target.exists():
                shutil.rmtree(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(backup, target)
        elif not saved.get('target_moved') and target.exists():
            shutil.rmtree(target)
        if saved.get('old_state') is None:
            state.unlink(missing_ok=True)
        else:
            atomic_record(state, saved['old_state'])
    journal.unlink()


def install_tree(project, name, source, row):
    project = Path(project).resolve()
    if name not in NAMES:
        raise ValueError('Unknown UI provider')
    incoming = inventory(source)
    restore_interrupted(project, name)
    target = skill_target(project, name)
    state_path = safe(project, '.trellis/personal/ui-tools/' + name + '.json')
    previous = load(state_path) if state_path.exists() else {}
    old_files = previous.get('files', {})
    for relative in old_files:
        if Path(relative).is_absolute() or '\\' in relative or '..' in Path(relative).parts:
            raise ValueError('Invalid skill manifest path: ' + relative)
    conflicts = []
    for relative in sorted(set(incoming) | set(old_files)):
        path = safe(project, '.agents/skills/' + name + '/' + relative)
        actual = digest(path.read_bytes()) if path.is_file() else None
        if path.exists() and not path.is_file():
            conflicts.append(relative)
        elif actual is not None and actual not in {old_files.get(relative), incoming.get(relative)}:
            conflicts.append(relative)
        elif relative in old_files and actual is None and relative in incoming:
            conflicts.append(relative)
    if conflicts:
        candidate = safe(project, '.trellis/personal/ui-tools/candidates/' + name + '-' + stamp())
        shutil.copytree(source, candidate)
        return {'status': 'conflicts', 'files': conflicts,
                'candidate': str(candidate.relative_to(project)), 'installation': 'preserved_local_changes'}
    if target.exists() and all((target / key).is_file() and digest((target / key).read_bytes()) == value
                               for key, value in incoming.items()) and not (set(old_files) - set(incoming)):
        record = {**row, 'files': incoming, 'skill': str(target), 'installation': 'reused'}
        atomic_record(state_path, record)
        return {'status': 'ready', **record}
    target.parent.mkdir(parents=True, exist_ok=True)
    transaction = stamp()
    stage = Path(tempfile.mkdtemp(prefix=name + '-', dir=str(target.parent)))
    backup = safe(project, '.trellis/personal/ui-tools/backups/' + name + '-' + transaction)
    journal = safe(project, '.trellis/personal/ui-tools/' + name + '-transaction.json')
    saved = {'transaction': transaction, 'backup': str(backup.relative_to(project)),
             'old_state': previous or None, 'target_moved': target.exists()}
    try:
        if target.exists():
            # Inspect even unowned extra files before copying; a link must not
            # make an update read or write outside this project.
            inventory(target)
            shutil.copytree(target, stage, dirs_exist_ok=True)
        for relative in set(old_files) - set(incoming):
            (stage / relative).unlink(missing_ok=True)
        shutil.copytree(source, stage, dirs_exist_ok=True)
        atomic_record(journal, saved)
        if target.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            os.replace(target, backup)
        os.replace(stage, target)
        record = {**row, 'files': incoming, 'skill': str(target), 'transaction': transaction,
                  'installation': 'updated' if previous else 'installed'}
        atomic_record(state_path, record)
        journal.unlink()
        return {'status': 'ready', **record}
    except BaseException:
        if journal.exists():
            restore_interrupted(project, name)
        raise
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def package_root(binary, expected):
    for parent in Path(binary).resolve().parents:
        metadata = parent / 'package.json'
        if metadata.is_file() and load(metadata).get('name') == expected:
            return parent
    raise RuntimeError('Cannot identify provider package: ' + expected)


def pinned_checkout(project, row):
    reference = row['source_ref']
    if not re.fullmatch(r'[0-9a-f]{40}', reference):
        raise ValueError('UI source must use a fixed Git commit')
    directory = safe(project, '.trellis/personal/ui-tools/bundles/' + row['bin'] + '-' + reference)
    marker = directory / '.source.json'
    if directory.exists():
        if not marker.is_file():
            raise RuntimeError('Existing provider cache has no owned source manifest')
        saved = load(marker)
        if saved['source_ref'] != reference:
            raise RuntimeError('Provider source cache differs from the locked commit')
        for relative, expected in saved['files'].items():
            path = directory / relative
            if '..' in Path(relative).parts or Path(relative).is_absolute() or path.is_symlink():
                raise ValueError('Invalid provider cache path')
            if not path.is_file() or digest(path.read_bytes()) != expected:
                raise RuntimeError('Provider cache was modified: ' + relative)
        return directory
    directory.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='source-', dir=str(directory.parent)))
    repository = row['source'].removeprefix('https://github.com/')
    if row['source'] != 'https://github.com/' + repository or repository.count('/') != 1:
        raise ValueError('Unsupported UI source origin')
    try:
        if row['bin'] == 'impeccable':
            archive = stage / 'source.zip'
            bounded_fetch(project, 'https://codeload.github.com/' + repository + '/zip/' + reference,
                          archive, row['bin'] + '-source-download')
            extract_skill_archive(archive, stage, '.agents/skills/impeccable')
            payload_hash = digest(archive.read_bytes())
            archive.unlink()
        else:
            license_file = stage / 'LICENSE'
            bounded_fetch(project, 'https://raw.githubusercontent.com/' + repository + '/' + reference + '/LICENSE',
                          license_file, row['bin'] + '-license-download')
            payload_hash = digest(license_file.read_bytes())
        files = {path.relative_to(stage).as_posix(): digest(path.read_bytes())
                 for path in sorted(stage.rglob('*')) if path.is_file()}
        write(stage / '.source.json', json_bytes({'source_ref': reference, 'source': row['source'],
                                                'download_sha256': payload_hash, 'files': files}))
        os.replace(stage, directory)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return directory


def bounded_fetch(project, url, destination, label):
    # A process deadline covers DNS and redirects as well as the socket read.
    code = '''import pathlib,sys,urllib.request
request=urllib.request.Request(sys.argv[1],headers={"User-Agent":"personal-trellis-library/1.0"})
with urllib.request.urlopen(request,timeout=15) as response:
    with pathlib.Path(sys.argv[2]).open("wb") as output:
        total=0
        while True:
            chunk=response.read(1024*1024)
            if not chunk: break
            total+=len(chunk)
            if total>128*1024*1024: raise ValueError("UI source download exceeds 128 MiB")
            output.write(chunk)
'''
    run(project, [sys.executable, '-c', code, url, str(destination)], label, timeout=60)


def extract_skill_archive(archive, destination, scope):
    with zipfile.ZipFile(archive) as contents:
        prefixes = {entry.filename.split('/')[0] for entry in contents.infolist()}
        if len(prefixes) != 1:
            raise ValueError('Unexpected UI source archive layout')
        prefix = next(iter(prefixes)) + '/'
        selected = []
        for entry in contents.infolist():
            relative = entry.filename.removeprefix(prefix)
            if relative != 'LICENSE' and not relative.startswith(scope + '/'):
                continue
            if entry.is_dir():
                continue
            mode = (entry.external_attr >> 16) & 0o170000
            if Path(relative).is_absolute() or '..' in Path(relative).parts or '\\' in relative or mode == 0o120000:
                raise ValueError('Unsafe UI source archive member')
            if entry.file_size > 32 * 1024 * 1024:
                raise ValueError('UI source file exceeds 32 MiB')
            selected.append((entry, relative))
        required = {'LICENSE', scope + '/SKILL.md'}
        if not required.issubset({relative for _, relative in selected}):
            raise ValueError('Archive is missing the selected skill or license')
        for entry, relative in selected:
            path = destination / relative
            write(path, contents.read(entry))
            path.chmod(0o755 if entry.external_attr >> 16 & 0o111 else 0o644)


def provider_environment(project, skill):
    return dict(os.environ, PWD=str(Path(project).resolve()), IMPECCABLE_SKILL_DIR=str(skill),
                IMPECCABLE_HOME=str(safe(project, '.trellis/personal/cache/impeccable')))


def prepare_provider(project, name, row, binary):
    source = pinned_checkout(project, row)
    stage_root = safe(project, '.trellis/personal/ui-tools/staging')
    stage_root.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=name + '-', dir=str(stage_root)))
    if name == 'impeccable':
        skill = stage / 'impeccable'
        upstream = source / '.agents/skills/impeccable'
        inventory(upstream)
        shutil.copytree(upstream, skill)
        root = package_root(binary, row['package'])
        system = {'Darwin': 'darwin', 'Linux': 'linux', 'Windows': 'windows'}.get(platform.system())
        arch = {'arm64': 'arm64', 'aarch64': 'arm64', 'x86_64': 'x64', 'AMD64': 'x64'}.get(platform.machine())
        if not system or not arch:
            raise RuntimeError('Impeccable engine not verified for this platform')
        target = system + '-' + arch
        engine_package = root / 'node_modules/@impeccable' / ('cli-' + target)
        # Optional platform packages are pinned separately from the npm shim.
        if not (engine_package / 'package.json').is_file() or load(engine_package / 'package.json')['version'] != row['engine_version']:
            raise RuntimeError('The pinned Impeccable platform engine is missing; do not report the npm shim as ready')
        executable = 'impeccable.exe' if system == 'windows' else 'impeccable'
        engine = engine_package / 'bin' / executable
        probe = run(project, [str(engine), 'engine-probe'], 'impeccable-engine-probe', timeout=20).strip()
        if probe != 'impeccable-engine ' + row['engine_version']:
            raise RuntimeError('Unexpected Impeccable engine handshake')
        destination = skill / 'scripts/bin' / target / executable
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(engine, destination)
        destination.chmod(0o755)
        write(skill / '.gitignore', b'scripts/bin/\n')
    else:
        code = 'import os,sys;os.chdir(sys.argv[1]);os.execv(sys.argv[2],sys.argv[2:])'
        run(project, [sys.executable, '-c', code, str(stage), str(binary), 'init', '--ai', 'codex', '--offline'],
            'uiux-generate-skill', timeout=60)
        skill = stage / '.agents/skills/ui-ux-pro-max'
    shutil.copy2(source / 'LICENSE', skill / 'LICENSE.upstream')
    return stage, skill


def probe_provider(project, name, skill, row):
    if name == 'ui-ux-pro-max':
        result = json.loads(run(project, [sys.executable, str(skill / 'scripts/search.py'),
                                'form validation', '--stack', 'vue', '--max-results', '2', '--json'],
                                'uiux-real-search', timeout=30))
        if not result.get('results') or result.get('stack') != 'vue':
            raise RuntimeError('UI UX Pro Max returned no representative stack guidance')
        return {'status': 'passed', 'query': 'form validation', 'stack': 'vue', 'count': result['count']}
    launcher = skill / ('scripts/impeccable.cmd' if platform.system() == 'Windows' else 'scripts/impeccable')
    if not os.access(launcher, os.X_OK):
        raise RuntimeError('Installed Impeccable launcher has lost executable permission; repair the owned installation')
    probe = run(project, [str(launcher), 'engine-probe'], 'impeccable-installed-handshake',
                env=provider_environment(project, skill), timeout=20).strip()
    if probe != 'impeccable-engine ' + row['engine_version']:
        raise RuntimeError('Installed skill cannot reach its pinned engine')
    fixture = safe(project, '.trellis/personal/ui-tools/probes/clean.css')
    write(fixture, b'.probe { display: block; padding: 8px; }\n')
    result = json.loads(run(project, [str(launcher), 'detect', '--json', str(fixture)],
                            'impeccable-real-detect', env=provider_environment(project, skill), timeout=30))
    return {'status': 'passed', 'engine': probe, 'detector_response': result,
            'scope': 'engine handshake and deterministic CSS scan; browser/UX review separate'}


def initialize_provider(project, name, row, force_local=False):
    binary, npm_status = npm_tool(project, row, force_local)
    if load(package_root(binary, row['package']) / 'package.json')['version'] != row['version']:
        raise RuntimeError('UI CLI package version differs from the lock')
    stage, skill = prepare_provider(project, name, row, binary)
    try:
        result = install_tree(project, name, skill, row)
        result['npm_installation'] = npm_status
        result['binary'] = str(binary)
        result['hook'] = 'not_enabled; use explicit detector until separately configured and trusted'
        result['client_discovery'] = 'files_ready_for_next_turn; actual client auto-selection not yet observed'
        if result['status'] == 'ready':
            result['probe'] = probe_provider(project, name, Path(result['skill']), row)
            result['status'] = 'installed_and_probed'
        return result
    finally:
        shutil.rmtree(stage)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--tool', choices=NAMES, required=True)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    project = args.project.resolve()
    skill = safe(project, '.agents/skills/' + args.tool)
    if args.tool == 'impeccable':
        launcher = skill / ('scripts/impeccable.cmd' if platform.system() == 'Windows' else 'scripts/impeccable')
        command = [str(launcher), *args.command]
        env = provider_environment(project, skill)
    else:
        command = [sys.executable, str(skill / 'scripts/search.py'), *args.command]
        env = None
    try:
        print(run(project, command, args.tool + '-explicit', env=env, timeout=120))
    except ToolCommandError as error:
        print(str(error), file=sys.stderr)
        return error.returncode
    return 0


if __name__ == '__main__':
    sys.exit(main())
