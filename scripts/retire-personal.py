#!/usr/bin/env python3
"""One-time retirement of legacy personal-owned files; preview unless --apply."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
import uuid

SKILLS = ('personal-project-init', 'personal-project-explore', 'personal-design')
PREFIXES = ('.trellis/spec/guides/personal/',) + tuple('.agents/skills/' + name + '/' for name in SKILLS)
START, END = '<!-- PERSONAL_TRELLIS:START -->', '<!-- PERSONAL_TRELLIS:END -->'
REFERENCES = ('.trellis/spec/guides/personal/', *SKILLS, 'PERSONAL_TRELLIS')
STATE = '.trellis/personal/install.json'
RECORDS = '.trellis/personal/retirement/'


def digest(content):
    return hashlib.sha256(content).hexdigest() if content is not None else None


def safe(project, name):
    relative = PurePosixPath(name)
    if (not name or relative.is_absolute() or '\\' in name or
            any(part in ('', '.', '..') for part in name.split('/'))):
        raise ValueError('Unsafe project path: ' + str(name))
    path = project.joinpath(*relative.parts)
    for parent in (path, *path.parents):
        if parent == project:
            break
        if parent.is_symlink():
            raise ValueError('Linked project path: ' + name)
    if path.exists() and not path.is_file():
        raise ValueError('Not a regular file: ' + name)
    return path


def read(project, name):
    path = safe(project, name)
    return path.read_bytes() if path.exists() else None


def write(project, name, content):
    path = safe(project, name)
    if content is None:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        stream.write(content)
        temporary = stream.name
    os.replace(temporary, path)


def encoded(value):
    return base64.b64encode(value).decode() if value is not None else None


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def plan(project, native_workflow=None, native_version=None):
    state_bytes = read(project, STATE)
    if state_bytes is None:
        raise ValueError('Legacy install.json required; no ownership inferred')
    state = json.loads(state_bytes)
    files = state.get('files')
    if not isinstance(files, dict):
        raise ValueError('Legacy files ownership map required')
    actions, changes, blockers = [], [], []

    def change(name, before, after, action):
        actions.append({'path': name, 'action': action})
        changes.append({'path': name, 'before': encoded(before), 'after': encoded(after),
                        'after_sha256': digest(after)})

    names = {name for name in files if isinstance(name, str) and name.startswith(PREFIXES)}
    # Report unknown files within exactly the retired namespaces, never traverse links.
    for prefix in PREFIXES:
        directory = project / prefix
        if any(p.is_symlink() for p in (directory, *directory.parents) if p != project and project in p.parents):
            names.add(prefix.rstrip('/'))
            continue
        if directory.is_dir():
            for parent, dirs, children in os.walk(directory, followlinks=False):
                linked = [name for name in dirs if (Path(parent) / name).is_symlink()]
                dirs[:] = [name for name in dirs if name not in linked]
                names.update((Path(parent) / name).relative_to(project).as_posix() for name in children + linked)
    for name in sorted(names):
        try:
            before = read(project, name)
        except ValueError as error:
            actions.append({'path': name, 'action': 'preserved', 'reason': str(error)})
            continue
        owner = files.get(name, {})
        if before is None:
            actions.append({'path': name, 'action': 'absent'})
        elif not isinstance(owner, dict) or digest(before) != owner.get('installed_sha256'):
            actions.append({'path': name, 'action': 'preserved', 'reason': 'modified_or_unowned'})
        else:
            change(name, before, None, 'remove')

    before = read(project, 'AGENTS.md')
    if before and (START.encode() in before or END.encode() in before):
        text = before.decode('utf-8')
        matches = list(re.finditer(re.escape(START) + '.*?' + re.escape(END), text, re.S))
        if (text.count(START) == text.count(END) == len(matches) == 1 and
                digest(matches[0].group().encode()) == state.get('agents_block_sha256')):
            match = matches[0]
            change('AGENTS.md', before, (text[:match.start()] + text[match.end():]).encode(), 'remove_personal_block')
        else:
            actions.append({'path': 'AGENTS.md', 'action': 'preserved', 'reason': 'modified_or_ambiguous_block'})
            blockers.append('AGENTS.md personal block remains active')

    before = read(project, '.trellis/workflow.md')
    owner = files.get('.trellis/workflow.md', {})
    if before is not None:
        reason = 'native_candidate_required'
        if not isinstance(owner, dict) or digest(before) != owner.get('installed_sha256'):
            reason = 'modified_or_unowned'
        elif native_workflow is not None:
            version = read(project, '.trellis/.version')
            if not native_version or version is None or version.decode().strip() != native_version:
                raise ValueError('Native candidate version must match project .trellis/.version')
            candidate = Path(native_workflow).read_bytes()
            if (not candidate.strip() or candidate == before or
                    any(token.encode() in candidate for token in REFERENCES)):
                raise ValueError('Expected an independently generated native workflow candidate')
            change('.trellis/workflow.md', before, candidate, 'restore_native_workflow')
            reason = None
        if reason:
            active = (isinstance(owner, dict) and digest(before) == owner.get('installed_sha256')) or any(
                token.encode() in before for token in REFERENCES)
            actions.append({'path': '.trellis/workflow.md',
                            'action': 'preserved' if active else 'unchanged', 'reason': reason})
            if active:
                blockers.append('Personal workflow remains active: ' + reason)
    return {'schema_version': 1, 'project': str(project), 'legacy_install_sha256': digest(state_bytes),
            'native_version': native_version, 'actions': actions, 'changes': changes,
            'blockers': blockers,
            'scope': 'personal specs/three skills/AGENTS block; optional workflow only',
            'legacy_runtime': 'preserved; no longer an active initialization entry'}


def execute(project, record, apply=False, restoring=False):
    if not restoring and record.get('blockers'):
        raise ValueError('Retirement blocked: ' + '; '.join(record['blockers']))
    changes = record['changes']
    actions, pending = [], []
    for row in changes:
        # Restore only paths permitted by the retirement scope, even for edited records.
        name = row['path']
        if not (name.startswith(PREFIXES) or name in ('AGENTS.md', '.trellis/workflow.md')):
            raise ValueError('Path outside retirement scope: ' + name)
        try:
            current = read(project, name)
        except ValueError as error:
            actions.append({'path': name, 'action': 'preserved', 'reason': str(error)})
            continue
        before = base64.b64decode(row['before'], validate=True) if row['before'] is not None else None
        after = base64.b64decode(row['after'], validate=True) if row['after'] is not None else None
        expected, desired = (after, before) if restoring else (before, after)
        if current == desired:
            actions.append({'path': name, 'action': 'already_applied'})
        elif current != expected:
            actions.append({'path': name, 'action': 'preserved', 'reason': 'changed_since_plan'})
        else:
            pending.append((name, desired))
            actions.append({'path': name, 'action': 'restore' if restoring else 'apply'})
    if apply and not restoring and any(row['action'] == 'preserved' for row in actions):
        raise ValueError('Retirement blocked: files changed since plan; no changes applied')
    if apply:
        for name, desired in pending:
            write(project, name, desired)
    return actions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--native-workflow', type=Path)
    parser.add_argument('--native-version')
    parser.add_argument('--restore', help='Retirement UUID to restore')
    args = parser.parse_args()
    project = args.project.resolve()
    try:
        if args.restore:
            if not re.fullmatch(r'[0-9a-f]{32}', args.restore):
                raise ValueError('Invalid retirement UUID')
            record = json.loads(read(project, RECORDS + args.restore + '.json'))
            if record.get('project') != str(project):
                raise ValueError('Recovery record belongs to another project')
            result = {'mode': 'restore' if args.apply else 'restore_preview',
                      'actions': execute(project, record, args.apply, restoring=True)}
        else:
            record = plan(project, args.native_workflow, args.native_version)
            result = dict(record, mode='apply' if args.apply else 'preview')
            if args.apply and record['blockers']:
                result.update(status='blocked')
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 2
            if args.apply:
                revision = uuid.uuid4().hex
                name = RECORDS + revision + '.json'
                # Persist every before-image before modifying any consumer asset.
                write(project, name, json_bytes(dict(record, status='prepared')))
                applied = execute(project, record, apply=True)
                write(project, name, json_bytes(dict(record, status='applied', applied=applied)))
                result.update(revision=revision, recovery=name, applied=applied)
        incomplete = any(row['action'] == 'preserved' for row in result.get('actions', []))
        result['status'] = 'partial' if incomplete else 'complete'
        if result.get('blockers'):
            result['status'] = 'blocked'
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if args.apply and incomplete else 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
