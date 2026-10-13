"""Acquire data-only stack profiles, then project them into scoped draft rules."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import time
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

from stack_facts import major_set

LIMIT = 2_000_000
TIMEOUT = 20
NAME = re.compile(r'[a-z][a-z0-9-]{0,63}')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def https_url(value):
    if not isinstance(value, str):
        raise ValueError('Source URL must be a string')
    parsed = urlsplit(value)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
            or parsed.query or parsed.fragment):
        raise ValueError('Source must be a credential-free HTTPS URL without query/fragment')
    return value


def relative(value):
    if not isinstance(value, str):
        raise ValueError('Source path must be a string')
    path = PurePosixPath(value)
    if not value or path.is_absolute() or '..' in path.parts or '\\' in value:
        raise ValueError('Source path must remain inside its registry')
    return path.as_posix()


def read_local(root, value):
    path = root / relative(value)
    if any(parent.is_symlink() for parent in (path, *path.parents) if parent != root.parent):
        raise ValueError('Linked local source is not supported')
    if not path.is_file() or path.stat().st_size > LIMIT:
        raise ValueError('Local source missing or oversized: ' + value)
    return path.read_bytes()


def fetch(url, timeout=TIMEOUT):
    """A child deadline also bounds DNS, stalled sockets and full response time."""
    https_url(url)
    try:
        result = subprocess.run([sys.executable, str(Path(__file__).resolve()), '_fetch', url],
                                capture_output=True, timeout=max(0.1, min(TIMEOUT, timeout)))
    except subprocess.TimeoutExpired:
        raise OSError('source_download_timeout') from None
    if result.returncode:
        raise OSError('source_download_failed: ' + result.stderr.decode('utf-8', errors='replace')[:240])
    if len(result.stdout) > LIMIT:
        raise ValueError('Source exceeds byte limit')
    return result.stdout


def cached(project, url, expected, offline, io, deadline):
    https_url(url)
    if not re.fullmatch(r'[0-9a-f]{64}', expected):
        raise ValueError('Resource requires a SHA-256 digest')
    base = '.trellis/personal/cache/specs/' + expected
    content = io.safe(project, base + '.txt')
    meta = io.safe(project, base + '.json')
    if content.exists():
        data = content.read_bytes()
        if sha(data) != expected:
            raise ValueError('Cached source was modified')
        record = json.loads(meta.read_text()) if meta.is_file() else {}
        return data, {'transport': 'verified_cache', 'retrieved_at': record.get('retrieved_at', 'unknown'),
                      'cache_path': base + '.txt'}
    if offline:
        raise OSError('offline_cache_miss')
    if time.monotonic() >= deadline:
        raise OSError('source_budget_exhausted')
    data = fetch(url, deadline - time.monotonic())
    if sha(data) != expected:
        raise ValueError('Downloaded source digest does not match the registry')
    data.decode('utf-8')
    record = {'url': url, 'sha256': expected,
              'retrieved_at': datetime.now(timezone.utc).isoformat(timespec='seconds')}
    io.write(content, data)
    io.write(meta, (json.dumps(record, ensure_ascii=False, indent=2) + '\n').encode())
    return data, {**record, 'transport': 'https_verified', 'cache_path': base + '.txt'}


def registry_locator(value):
    match = re.fullmatch(r'gh:([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)(/[^#]+)?#([0-9a-f]{40})', value)
    if not match:
        raise ValueError('Remote stack registry requires gh:OWNER/REPO[/subdir]#FULL_COMMIT_SHA')
    owner, repo, folder, commit = match.groups()
    folder = relative(folder[1:]) + '/' if folder else ''
    base = 'https://raw.githubusercontent.com/' + owner + '/' + repo + '/' + commit + '/' + quote(folder)
    return base, commit


def validate_registry(data, root=None, remote_base=None, ref=None):
    if not isinstance(data, dict) or data.get('schema_version') != 1 or not isinstance(data.get('profiles'), list):
        raise ValueError('Unsupported stack registry schema')
    ids = set()
    for item in data['profiles']:
        if (not isinstance(item, dict) or not isinstance(item.get('id'), str)
                or not re.fullmatch(r'[a-z][a-z0-9.-]{0,127}', item['id'])):
            raise ValueError('Invalid profile ID')
        if item['id'] in ids or not isinstance(item.get('stack'), str) or not NAME.fullmatch(item['stack']):
            raise ValueError('Duplicate ID or invalid stack name')
        ids.add(item['id'])
        if item.get('kind') not in {'personal', 'official', 'opensource'}:
            raise ValueError('Unknown source kind')
        majors = item.get('major_versions')
        if type(item.get('version_independent', False)) is not bool:
            raise ValueError('version_independent must be a boolean')
        if majors is not None and (not isinstance(majors, list) or any(type(number) is not int or number < 0 for number in majors)):
            raise ValueError('major_versions must contain non-negative integers')
        if not item.get('version_independent') and (not isinstance(majors, list) or not majors
                or any(type(number) is not int or number < 0 for number in majors)):
            raise ValueError('Profile requires explicit compatible majors')
        source = item.get('source', {})
        if (not isinstance(source, dict) or ('path' in source) == ('url' in source)
                or not isinstance(source.get('sha256'), str) or not re.fullmatch(r'[0-9a-f]{64}', source['sha256'])
                or not isinstance(item.get('license'), str) or not item['license']
                or not isinstance(item.get('coverage'), list) or not item['coverage']
                or any(not isinstance(value, str) for value in item['coverage'])):
            raise ValueError('Profile requires one source locator, digest, license and coverage')
        if 'path' in source:
            relative(source['path'])
        else:
            https_url(source['url'])
            if not source.get('ref'):
                raise ValueError('Remote resource requires a version/ref')
        if item['kind'] != 'personal' and not item.get('adaptation'):
            raise ValueError('Reference documents need a maintained adaptation guide')
        if item.get('adaptation'):
            relative(item['adaptation'])
        item['_root'], item['_remote_base'], item['_registry_ref'] = root, remote_base, ref
    return data['profiles']


def external_registry(project, locator, offline, io, deadline):
    if not locator:
        return [], None
    if locator.startswith('gh:'):
        base, ref = registry_locator(locator)
        url = base + 'stack-sources.json'
        key = sha(url.encode())
        path = io.safe(project, '.trellis/personal/cache/specs/registries/' + key + '.json')
        if path.is_file():
            raw = path.read_bytes()
            record = json.loads(io.safe(project, '.trellis/personal/cache/specs/registries/' + key + '.sha.json').read_text())
            if sha(raw) != record['sha256']:
                raise ValueError('Cached registry was modified')
        elif offline:
            raise OSError('offline_registry_cache_miss')
        else:
            if time.monotonic() >= deadline:
                raise OSError('source_budget_exhausted')
            raw = fetch(url, deadline - time.monotonic())
            # Validate before admitting a registry to the local cache.
            validate_registry(json.loads(raw), remote_base=base, ref=ref)
            io.write(path, raw)
            io.write(io.safe(project, '.trellis/personal/cache/specs/registries/' + key + '.sha.json'),
                     (json.dumps({'sha256': sha(raw), 'ref': ref}) + '\n').encode())
        return validate_registry(json.loads(raw), remote_base=base, ref=ref), {'locator': locator, 'sha256': sha(raw), 'ref': ref}
    path = Path(locator).resolve()
    if not path.is_file() or path.stat().st_size > LIMIT:
        raise ValueError('Local stack registry missing or oversized')
    raw = path.read_bytes()
    return validate_registry(json.loads(raw), root=path.parent, ref='local:' + sha(raw)), {'locator': 'local registry', 'sha256': sha(raw)}


def compatible(profile, version):
    if profile.get('version_independent'):
        return True
    majors = major_set(version)
    return None if not majors else majors.issubset(set(profile.get('major_versions', [])))


def acquire(profile, project, library, offline, io, deadline):
    source = profile['source']
    if 'url' in source:
        url, ref = source['url'], source['ref']
    elif profile.get('_remote_base'):
        url, ref = profile['_remote_base'] + quote(relative(source['path'])), profile['_registry_ref']
    else:
        data = read_local(profile['_root'], source['path'])
        if sha(data) != source['sha256']:
            raise ValueError('Local source digest mismatch')
        return data, {'url': 'local:' + relative(source['path']), 'ref': profile['_registry_ref'],
                      'sha256': sha(data), 'transport': 'local', 'retrieved_at': 'local snapshot'}
    data, record = cached(project, url, source['sha256'], offline, io, deadline)
    return data, {**record, 'url': url, 'ref': ref, 'sha256': source['sha256']}


def scopes(detected, stacks, versions):
    grouped, found = {}, set()
    for package in detected['packages']:
        for stack in sorted(set(package['stacks']) | set(package.get('databases', []))):
            found.add(stack)
            version = package['versions'].get(stack)
            version_facts = package.get('version_facts', {}).get(stack, [
                {'version': version, 'raw': package.get('raw_versions', {}).get(stack),
                 'evidence': package.get('version_evidence', {}).get(stack)}] if version else [])
            version_conflict = any(fact['version'] != version and
                                   not declaration_matches(fact['version'], version) and
                                   not declaration_matches(version, fact['version']) for fact in version_facts)
            declared = versions.get(stack)
            conflict = bool(version and declared and version != declared and
                            not declaration_matches(version, declared))
            facts = {'stack': stack, 'scope': package.get('scope', str(Path(package['path']).parent)),
                           'manifest': package['path'], 'version': version or declared,
                           'version_evidence': package.get('version_evidence', {}).get(stack, 'explicit declaration' if declared else 'unknown'),
                           'commands': package.get('commands', []), 'declaration_conflict': conflict,
                           'raw_version': package.get('raw_versions', {}).get(stack),
                           'version_facts': version_facts,
                           'version_conflict': version_conflict,
                           'detection_evidence': package.get('detection_evidence', {}).get(stack, []),
                           'diagnostics': package.get('diagnostics', []),
                           'manifests': [package['path']]}
            if declared and not conflict and major_set(version) is None:
                facts['version'] = declared
                facts['version_evidence'] += '; compatible explicit target declaration'
            key = (facts['scope'], stack)
            if key in grouped:
                previous = grouped[key]
                previous['manifests'].append(package['path'])
                previous['commands'] = sorted(set(previous['commands'] + facts['commands']))
                previous['diagnostics'] = sorted(set(previous['diagnostics'] + facts['diagnostics']))
                previous['detection_evidence'] += facts['detection_evidence']
                previous['declaration_conflict'] |= conflict
                previous['version_conflict'] |= facts['version_conflict']
                previous['version_facts'] += facts['version_facts']
                if previous['version'] and facts['version'] and previous['version'] != facts['version']:
                    if declaration_matches(previous['version'], facts['version']):
                        previous['version'], previous['version_evidence'] = facts['version'], facts['version_evidence']
                        previous['raw_version'] = facts['raw_version']
                    elif not declaration_matches(facts['version'], previous['version']):
                        previous['version_conflict'] = True
                        previous['diagnostics'].append('Conflicting version facts in this scope; reconcile manifest/runtime declarations')
                if not previous['version'] and facts['version']:
                    previous['version'], previous['version_evidence'] = facts['version'], facts['version_evidence']
                    previous['raw_version'] = facts['raw_version']
            else:
                grouped[key] = facts
    for stack in sorted(set(stacks) - found):
        grouped[('.', stack)] = {'stack': stack, 'scope': '.', 'manifest': None, 'version': versions.get(stack),
                       'version_evidence': 'explicit declaration' if versions.get(stack) else 'unknown',
                       'commands': [], 'declaration_conflict': False, 'manifests': []}
    return list(grouped.values())


def declaration_matches(constraint, declared):
    """Conservative confirmation; exact resolved dependencies remain authoritative."""
    if not re.fullmatch(r'\d+(?:\.\d+){0,2}', declared):
        return False
    if re.fullmatch(r'\d+(?:\.\d+){0,2}', constraint):
        return constraint == declared
    if constraint.startswith(('^', '~')):
        if major_set(constraint) != major_set(declared):
            return False
        minimum = constraint[1:].split('.')
        actual = declared.split('.')
        if any(not part.isdigit() for part in minimum):
            return False
        low = tuple(int(part) for part in minimum) + (0,) * (3 - len(minimum))
        value = tuple(int(part) for part in actual) + (0,) * (3 - len(actual))
        if constraint[0] == '~':
            index = 0 if len(minimum) == 1 else 1
        else:
            index = next((index for index, part in enumerate(low) if part), len(minimum) - 1)
        upper = low[:index] + (low[index] + 1,) + (0,) * (2 - index)
        return low <= value < upper
    terms = re.findall(r'(>=|>|<=|<|==|=)\s*(\d+(?:\.\d+){0,2})', constraint)
    if not terms or re.sub(r'(>=|>|<=|<|==|=)\s*\d+(?:\.\d+){0,2}|[ ,]', '', constraint):
        return False
    pieces = declared.split('.')
    value = tuple(int(part) for part in pieces) + (0,) * (3 - len(pieces))
    for op, number in terms:
        pieces = number.split('.')
        target = tuple(int(part) for part in pieces) + (0,) * (3 - len(pieces))
        if not {'>=': value >= target, '>': value > target, '<=': value <= target,
                '<': value < target, '==': value == target, '=': value == target}[op]:
            return False
    return True


def markdown(row, body):
    lines = ['# ' + row['stack'] + ' / ' + row['scope'], '',
             '**State:** ' + row['status'] + '; project source review required.', '',
             '## Project facts', '', '- Package: `' + row['scope'] + '`',
             '- Manifest: `' + (row['manifest'] or 'not created; declared target') + '`',
             '- Version constraint: `' + (row['version'] or 'unknown') + '`',
             '- Evidence: ' + row['version_evidence'], '', '## Acquired guideline', '', body.rstrip(), '',
             '## Adaptation and checks', '',
             '- Read current local rules and representative source in this package; preserve their authority.',
             '- Confirm actual module boundaries, error/types, tests and applicable dependency versions.',
             '- Resolve recorded gaps before using version-sensitive APIs. Do not upgrade application dependencies.',
             '- Validate from the listed package; confirm workspace/reactor scope before running a command.']
    lines += ['- Discovered verification entry: `' + command + '` (not executed by initialization).' for command in row['commands']]
    if not row['commands']:
        lines.append('- Verification entry not found. Determine it from project configuration; do not invent a passing command.')
    if row.get('raw_version'):
        lines.append('- Raw manifest version: `' + row['raw_version'] + '` (normalization does not erase evidence).')
    lines += ['- Detection diagnostic: ' + message for message in row.get('diagnostics', [])]
    if row.get('version_state') in {'unknown', 'unbounded_or_unparseable'}:
        lines.append('- Release compatibility remains pending; COMMON guidance does not supply a missing runtime/API version.')
    source = row.get('source')
    if source:
        lines += ['', '## Provenance', '', '- Profile: `' + row['profile_id'] + '` (' + row['kind'] + ')',
                  '- Source: ' + source['url'], '- Ref: `' + str(source['ref']) + '`',
                  '- SHA-256: `' + source['sha256'] + '`', '- License: ' + row['license'],
                  '- Coverage: ' + '; '.join(row['coverage'])]
    return ('\n'.join(lines) + '\n').encode()


def resolve(project, library, catalog, detected, stacks, versions, registry, offline, io, budget=60):
    for stack in list(stacks) + list(versions):
        if not NAME.fullmatch(stack):
            raise ValueError('Invalid stack name: ' + stack)
    if any(not isinstance(value, str) or len(value) > 200 for value in versions.values()):
        raise ValueError('Declared versions must be bounded strings')
    deadline = time.monotonic() + budget
    errors = []
    try:
        external, registry_record = external_registry(project, registry, offline, io, deadline)
    except OSError as error:
        external, registry_record = [], {'locator': registry, 'state': str(error)}
        errors.append(str(error))
    bundled = []
    for entry in catalog['entries']:
        if entry['category'] != 'stacks':
            continue
        content = io.safe(library, entry['path']).read_bytes()
        for stack in entry['stacks']:
            bundled.append({'id': entry['id'], 'stack': stack, 'kind': 'personal',
                            'version_independent': entry.get('version_independent', False),
                            'major_versions': entry.get('major_versions', []),
                            'source': {'path': entry['path'], 'sha256': sha(content)},
                            'license': 'personal draft; publication license pending',
                            'coverage': entry.get('coverage', ['general conventions; project adaptation required']),
                            'baseline_kind': entry.get('baseline_kind'),
                            '_root': library, '_registry_ref': 'library:' + catalog['version'], '_bundled': True})
    official = [profile for profile in validate_registry(json.loads((library / 'stack-sources.json').read_text()),
                root=library, ref='library:' + catalog['version']) if profile['kind'] != 'personal']
    ordered = ([profile for profile in external if profile['kind'] == 'personal'] + bundled +
               [profile for profile in external if profile['kind'] == 'official'] + official +
               [profile for profile in external if profile['kind'] == 'opensource'])
    assets, entries, rows = {}, [], []
    for facts in scopes(detected, set(stacks) | set(versions), versions):
        row = {**facts, 'attempts': [], 'source': None, 'adaptation_state': 'pending_project_review'}
        row['version_state'] = 'unknown' if not row['version'] else 'major_constrained' if major_set(row['version']) else 'unbounded_or_unparseable'
        body = 'No compatible guideline acquired. Use focused official-source research and record unsupported contracts.'
        candidates = [profile for profile in ordered if profile['stack'] == row['stack']]
        row['status'] = 'missing_source' if not candidates else 'version_unconfirmed'
        if row.get('version_conflict'):
            row['status'] = 'version_conflict'
        elif row['declaration_conflict']:
            row['status'] = 'declaration_conflict'
        else:
            for profile in candidates:
                match = compatible(profile, row['version'])
                if not match:
                    reason = 'version_unconfirmed' if match is None else 'version_mismatch'
                    row['attempts'].append({'profile_id': profile['id'], 'state': reason})
                    if row['status'] != 'acquired':
                        row['status'] = reason
                    continue
                try:
                    raw, record = acquire(profile, project, library, offline, io, deadline)
                    text = raw.decode('utf-8')
                except (OSError, ValueError) as error:
                    row['attempts'].append({'profile_id': profile['id'], 'state': 'acquisition_failed', 'reason': str(error)})
                    row['status'] = 'acquisition_failed'
                    continue
                row.update({'status': 'acquired', 'profile_id': profile['id'], 'kind': profile['kind'],
                            'source': record, 'license': profile['license'], 'coverage': profile['coverage'],
                            'version_policy': 'version_independent' if profile.get('version_independent') else 'major_scoped'})
                row['bundled_rule_id'] = profile['id'] if profile.get('_bundled') else None
                row['baseline_kind'] = profile.get('baseline_kind', 'official_reference' if profile['kind'] != 'personal' else 'project_guideline')
                row['attempts'].append({'profile_id': profile['id'], 'state': 'acquired'})
                if profile['kind'] == 'personal':
                    body = ('Read the bundled base guideline for this stack; this file adds package-specific facts.'
                            if profile.get('_bundled') else text)
                else:
                    # The downloaded page is reference data, never a workflow or executable instruction.
                    body = read_local(library, profile['adaptation']).decode('utf-8')
                    row['reference_state'] = 'downloaded_reference_not_executable'
                break
        if row['status'] != 'acquired':
            if row['status'] not in {'declaration_conflict', 'version_conflict'} and row['attempts']:
                states = {attempt['state'] for attempt in row['attempts']}
                row['status'] = next(state for state in ('acquisition_failed', 'version_unconfirmed', 'version_mismatch') if state in states)
            row['research_query'] = row['stack'] + ' ' + (row['version'] or '') + ' official coding conventions project structure testing'
        key = sha((row['scope'] + '\0' + row['stack']).encode())[:12]
        target = 'guides/personal/stacks/' + row['stack'] + '/project-' + key + '.md'
        row['target'] = '.trellis/spec/' + target
        assets[row['target']] = markdown(row, body)
        entries.append({'id': 'project.' + row['stack'] + '.' + key, 'category': 'stacks', 'target': target,
                        'title': row['stack'] + ' / ' + row['scope'], 'summary': row['status'] + ': ' + row['scope']})
        rows.append(row)
    report = {'schema_version': 1, 'date': datetime.now(timezone.utc).date().isoformat(),
              'detection_diagnostics': detected.get('diagnostics', []),
              'registry': registry_record, 'offline': offline, 'registry_errors': errors, 'packages': rows,
              'acquisition_complete': bool(rows) and not errors and all(row['status'] == 'acquired' for row in rows),
              'adaptation_complete': False, 'adaptation_state': 'pending_project_review'}
    report['state'] = 'acquired' if report['acquisition_complete'] else 'incomplete' if rows else 'stack_undetermined'
    return report, assets, entries


def chinese_report(report):
    labels = {'acquired': '已获取，待项目核对', 'missing_source': '未命中来源', 'version_unconfirmed': '版本待确定',
              'version_mismatch': '版本不匹配', 'acquisition_failed': '获取受限', 'declaration_conflict': '声明与项目版本冲突',
              'version_conflict': '同包清单版本冲突'}
    states = {'acquired': '已获取', 'incomplete': '仍有缺口', 'stack_undetermined': '技术栈待确定'}
    lines = ['# 技术栈规范来源与适配记录', '', '> 获取状态：' + states[report['state']] + '；适配状态：待 AI 核对项目源码。', '',
             '| 技术栈 | 包/层 | 版本证据 | 获取结果 | 规范 |', '|---|---|---|---|---|']
    for row in report['packages']:
        label = '保留原规范；新候选待处理' if row.get('candidate') else labels[row['status']]
        target = row.get('candidate', row['target'])
        lines.append('| ' + row['stack'] + ' | `' + row['scope'] + '` | `' + (row['version'] or '未确定').replace('|', '\\|') +
                     '` | ' + label + ' | [查看规范](../' + target.removeprefix('.trellis/') + ') |')
    lines += ['', '## 来源与缺口', '']
    if not report['packages']:
        lines.append('- 空白项目尚未声明技术栈。先讨论选型，再用 --stacks / --stack-versions 查询。')
    for row in report['packages']:
        if row['source']:
            lines.append('- ' + row['stack'] + ' / ' + row['scope'] + '：' + row['source']['url'] +
                         '；ref `' + str(row['source']['ref']) + '`；SHA-256 `' + row['source']['sha256'] + '`。')
        if row.get('research_query'):
            lines.append('- 待定向检索：`' + row['research_query'] + '`。使用已有网页/MCP 阅读官方原文，整理为来源 profile 后重新查询。')
        for attempt in row['attempts']:
            if attempt['state'] != 'acquired':
                lines.append('- ' + attempt['profile_id'] + '：' + attempt['state'] + ('；' + attempt['reason'] if attempt.get('reason') else '') + '。')
        if row.get('version_state') in {'unknown', 'unbounded_or_unparseable'}:
            lines.append('- ' + row['stack'] + ' / ' + row['scope'] + '：版本未完全确定；COMMON 获取成功仅提供共性机制，发布版本/API 兼容仍待核对。')
    lines.extend('- 检测诊断：' + message for message in report.get('detection_diagnostics', []))
    lines.extend('- 个人 registry：' + error for error in report['registry_errors'])
    lines += ['', '获取和摘要验证通过不等于项目工程适配完成。AI 需核对真实目录、模块/接口、错误和测试入口，补充本地调整及验证证据；已有规范优先保留。',
              '数据库驱动版本不能当作数据库服务端版本；未发现的命令不伪造。初始化不执行下载资料中的代码或修改应用依赖。', '']
    return '\n'.join(lines).encode()


if __name__ == '__main__' and len(sys.argv) == 3 and sys.argv[1] == '_fetch':
    try:
        with urlopen(Request(https_url(sys.argv[2]), headers={'User-Agent': 'personal-trellis-specs/1.0'}), timeout=10) as response:
            https_url(response.url)
            data = response.read(LIMIT + 1)
            if len(data) > LIMIT:
                raise ValueError('Source exceeds byte limit')
            sys.stdout.buffer.write(data)
    except Exception as error:
        print(type(error).__name__ + ': ' + str(error)[:200], file=sys.stderr)
        sys.exit(1)
