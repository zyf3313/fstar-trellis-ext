#!/usr/bin/env python3
"""Build or verify a deterministic local release candidate (Python 3.9+)."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

LIBRARY = Path(__file__).resolve().parent.parent
MANIFEST = 'release-manifest.json'
EXCLUDED = {'node_modules', '__pycache__', 'dist', '.git', '.tmp', '.tools',
            '.cache', '.runtime', '.trellis', '.codex', '.qmd', '.codegraph',
            'backups', 'cache', 'evidence', 'private', 'credentials', 'config-candidates'}
RUNTIME_SOURCES = {'examples/ui-module/runtime/' + name for name in
                   ('prototype.js', 'gallery.html', 'gallery.js', 'requirements.css', 'prototype.html', 'styles.css')}


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def sha256(content):
    return hashlib.sha256(content).hexdigest()


def safe_name(name):
    path = PurePosixPath(name)
    if (not name or '\\' in name or ':' in name or '\x00' in name or
            any(ord(c) < 32 for c in name) or path.is_absolute() or
            any(part in ('', '.', '..') for part in name.split('/'))):
        raise ValueError('Unsafe archive path: ' + repr(name))
    return path


def forbidden(name):
    path = safe_name(name)
    return (bool(set(path.parts) & EXCLUDED) or
            ('runtime' in path.parts and name not in RUNTIME_SOURCES) or
            path.name.startswith('.env') or
            path.suffix.lower() in {'.pyc', '.pyo', '.pem', '.key', '.p12', '.pfx', '.sqlite', '.db', '.log'} or
            path.name in {'install.json', '.npmrc', '.DS_Store', 'config.json', 'config.toml', 'credentials.json'} or
            '.new.' in path.name or path.name.endswith(('-state.json', '-report.json', '.bak')))


def validate_policy(data):
    if (data.get('schema_version') != 1 or data.get('status') != 'local_candidate' or
            data.get('license_decision') != 'pending'):
        raise ValueError('Unsupported local-candidate policy; license choice requires a reviewed policy change')
    names = []
    for key in ('files', 'directories'):
        if not isinstance(data.get(key), list) or not all(isinstance(name, str) for name in data[key]):
            raise ValueError('Policy assets must be lists of paths')
        for name in data[key]:
            if len(safe_name(name).parts) != 1 or forbidden(name):
                raise ValueError('Only safe explicit top-level assets may be allowed')
            names.append(name)
    if len(names) != len(set(names)):
        raise ValueError('Duplicate policy assets')
    required = data.get('required_files', [])
    if not isinstance(required, list) or not all(isinstance(name, str) for name in required):
        raise ValueError('Required assets must be a list of paths')
    for name in required:
        path = safe_name(name)
        if forbidden(name) or (name not in data['files'] and path.parts[0] not in data['directories']):
            raise ValueError('Required asset is not allowlisted: ' + name)
    return data


def policy(root):
    return validate_policy(json.loads((root / 'release-policy.json').read_text(encoding='utf-8')))


def require_assets(files, rules):
    required = set(rules['files']) | set(rules.get('required_files', []))
    if 'examples' in rules['directories']:
        required.update(RUNTIME_SOURCES)
    missing = required - set(files)
    if missing:
        raise ValueError('Missing required release assets: ' + ', '.join(sorted(missing)))


def inventory(root):
    rules = policy(root)
    files, excluded = {}, []
    for entry in sorted(root.iterdir()):
        if entry.name not in rules['files'] + rules['directories']:
            excluded.append({'path': entry.name, 'reason': 'not_allowlisted'})
    def visit(path):
        name = path.relative_to(root).as_posix()
        safe_name(name)
        # Do not traverse excluded dependency/cache trees, including their symlinks.
        if set(PurePosixPath(name).parts) & EXCLUDED or path.name.startswith('.env') or path.suffix in {'.pyc', '.pyo'}:
            excluded.append({'path': name, 'reason': 'dependency_cache_or_private'})
            return
        if path.is_symlink():
            raise ValueError('Symlink in allowed assets: ' + name)
        if path.is_dir():
            if forbidden(name):
                # The exact six runtime source files are individually approved below.
                if name != 'examples/ui-module/runtime':
                    raise ValueError('Runtime directory in allowed assets: ' + name)
            for child in sorted(path.iterdir()):
                visit(child)
        elif path.is_file():
            if forbidden(name):
                raise ValueError('Runtime/private/candidate file in allowed assets: ' + name)
            files[name] = path.read_bytes()
        else:
            raise ValueError('Non-regular or missing asset: ' + name)
    for name in sorted(rules['files'] + rules['directories']):
        visit(root / name)
    require_assets(files, rules)
    return files, sorted(excluded, key=lambda row: row['path'])


def build(root, output):
    root, output = root.resolve(), output.resolve()
    rules = policy(root)
    try:
        relative_output = output.relative_to(root)
    except ValueError:
        relative_output = None
    if relative_output is not None and (not relative_output.parts or relative_output.parts[0] in rules['directories']):
        raise ValueError('Release output must be outside allowed source directories')
    files, excluded = inventory(root)
    metadata = json.loads(files['library.json'])
    if metadata.get('publication') != 'not_published' or not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', metadata['version']):
        raise ValueError('Expected a versioned, unpublished local candidate')
    prefix = 'personal-trellis-' + metadata['version']
    manifest = {'schema_version': 1, 'name': metadata['name'], 'version': metadata['version'],
                'status': 'local_candidate', 'publication': 'not_published',
                'license_decision': 'pending', 'externally_publishable': False,
                'tested_trellis': metadata['tested_trellis'], 'python': metadata['python'],
                'archive_root': prefix, 'archive_format': 'zip-stored-fixed-1980',
                'files': [{'path': name, 'bytes': len(content), 'sha256': sha256(content)}
                          for name, content in sorted(files.items())]}
    manifest_bytes = json_bytes(manifest)
    output.mkdir(parents=True, exist_ok=True)
    archive = output / (prefix + '-local-candidate.zip')
    temporary = archive.with_suffix('.zip.tmp')
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_STORED) as bundle:
            for name, content in sorted({**files, MANIFEST: manifest_bytes}.items()):
                info = zipfile.ZipInfo(prefix + '/' + name, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                bundle.writestr(info, content)
        os.replace(temporary, archive)
    finally:
        if temporary.exists():
            temporary.unlink()
    digest = sha256(archive.read_bytes())
    archive.with_suffix('.manifest.json').write_bytes(manifest_bytes)
    archive.with_suffix('.zip.sha256').write_text(digest + '  ' + archive.name + '\n', encoding='ascii')
    return {'archive': str(archive), 'sha256': digest, 'files': len(files),
            'source_bytes': sum(map(len, files.values())), 'archive_bytes': archive.stat().st_size,
            'excluded': excluded, 'license_decision': 'pending', 'externally_publishable': False}


def verify(archive):
    with zipfile.ZipFile(archive) as bundle:
        members = bundle.infolist()
        names = [item.filename for item in members]
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive members')
        manifests = [name for name in names if name.endswith('/' + MANIFEST)]
        if len(manifests) != 1:
            raise ValueError('Expected exactly one release manifest')
        manifest = json.loads(bundle.read(manifests[0]))
        prefix = manifest['archive_root']
        safe_name(prefix)
        if len(PurePosixPath(prefix).parts) != 1 or manifest.get('schema_version') != 1:
            raise ValueError('Invalid manifest format/root')
        if (manifest.get('status') != 'local_candidate' or manifest.get('publication') != 'not_published' or
                manifest.get('license_decision') != 'pending' or manifest.get('externally_publishable') is not False):
            raise ValueError('Unexpected candidate publication/license state')
        rows = manifest['files']
        expected = {}
        for row in rows:
            name = row['path']
            safe_name(name)
            if name in expected or name == MANIFEST or forbidden(name):
                raise ValueError('Invalid/duplicate manifest asset: ' + name)
            expected[name] = row
        actual = {}
        for item in members:
            path = safe_name(item.filename)
            if path.parts[0] != prefix or len(path.parts) < 2:
                raise ValueError('Member outside manifest root')
            mode = item.external_attr >> 16
            if item.is_dir() or stat.S_IFMT(mode) not in (0, stat.S_IFREG):
                raise ValueError('Archive contains non-regular file')
            name = '/'.join(path.parts[1:])
            if name != MANIFEST:
                if forbidden(name):
                    raise ValueError('Forbidden archive asset: ' + name)
                content = bundle.read(item)
                actual[name] = {'path': name, 'bytes': len(content), 'sha256': sha256(content)}
        if actual != expected:
            raise ValueError('Archive manifest integrity mismatch')
        rules = validate_policy(json.loads(bundle.read(prefix + '/release-policy.json')))
        require_assets(actual, rules)
        metadata = json.loads(bundle.read(prefix + '/library.json'))
        if (not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', metadata['version']) or
                prefix != 'personal-trellis-' + metadata['version'] or
                any(manifest.get(key) != metadata.get(key) for key in
                    ('name', 'version', 'publication', 'tested_trellis', 'python'))):
            raise ValueError('Manifest/library metadata mismatch')
        for name in actual:
            top = PurePosixPath(name).parts[0]
            if name not in rules['files'] and top not in rules['directories']:
                raise ValueError('Archive asset is not allowlisted: ' + name)
    return {'status': 'verified', 'files': len(actual), 'sha256': sha256(Path(archive).read_bytes()),
            'license_decision': 'pending', 'externally_publishable': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'verify'])
    parser.add_argument('--library', type=Path, default=LIBRARY)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--archive', type=Path)
    args = parser.parse_args()
    if args.command == 'build' and args.output is None:
        parser.error('build requires --output')
    if args.command == 'verify' and args.archive is None:
        parser.error('verify requires --archive')
    try:
        result = build(args.library, args.output) if args.command == 'build' else verify(args.archive)
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(1, str(error) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
