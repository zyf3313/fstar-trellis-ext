#!/usr/bin/env python3
"""Install and inspect a portable personal Trellis library (Python >= 3.9)."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stack_facts
import stack_definitions
import stack_sources

LIBRARY = Path(__file__).resolve().parents[1]
IGNORED = {'.git', '.trellis', '.agents', '.codex', '.tmp', 'node_modules',
           'target', 'dist', 'build', '.venv', 'venv', 'vendor', '.worktrees',
           '.gradle', '.dart_tool', '.next', '.nuxt', '.output', '.svelte-kit',
           '.build', 'Pods', 'Carthage', 'DerivedData', '__pycache__'}


def stamp():
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe(root, relative):
    root = root.resolve()
    path = (root / relative).resolve()
    if Path(relative).is_absolute() or path == root or root not in path.parents:
        raise ValueError('Path must remain inside its owner: ' + str(relative))
    return path


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        tmp.write(content)
        name = tmp.name
    os.replace(name, path)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def catalog():
    data = load(LIBRARY / 'catalog.json')
    if not isinstance(data, dict) or data.get('schema_version') != 1 or not isinstance(data.get('entries'), list):
        raise ValueError('Unsupported personal catalog schema')
    entries = data['entries']
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get('id'), str) or not re.fullmatch(r'[a-z][a-z0-9.-]+', entry['id']):
            raise ValueError('Invalid rule ID')
        for key in ('stacks', 'capabilities', 'depends_on'):
            if not isinstance(entry.get(key, []), list) or any(not isinstance(value, str) for value in entry.get(key, [])):
                raise ValueError('Invalid rule selector/dependency: ' + entry['id'])
        if type(entry.get('default', False)) is not bool:
            raise ValueError('Rule default must be boolean')
    ids = {entry['id'] for entry in entries}
    if len(ids) != len(entries):
        raise ValueError('Duplicate rule ID')
    paths = set()
    for entry in entries:
        source = safe(LIBRARY, entry['path'])
        if not source.is_file():
            raise ValueError('Missing source: ' + entry['path'])
        target = str(safe(LIBRARY, entry['target']))
        if target in paths:
            raise ValueError('Duplicate target path: ' + entry['target'])
        paths.add(target)
        if set(entry.get('depends_on', [])) - ids:
            raise ValueError('Missing dependency for ' + entry['id'])
        if entry['category'] not in {'core', 'process', 'engineering', 'stacks', 'tools'}:
            raise ValueError('Unknown rule category')
    return data


def select(data, stacks=(), capabilities=(), only_default=False, all_rules=False):
    lookup = {entry['id']: entry for entry in data['entries']}
    chosen = set()
    visiting = set()

    def visit(rule_id):
        if rule_id in visiting:
            raise ValueError('Dependency cycle: ' + rule_id)
        if rule_id in chosen:
            return
        visiting.add(rule_id)
        for dependency in lookup[rule_id].get('depends_on', []):
            visit(dependency)
        visiting.remove(rule_id)
        chosen.add(rule_id)

    for entry in data['entries']:
        matches = set(entry.get('stacks', [])) & set(stacks)
        matches |= set(entry.get('capabilities', [])) & set(capabilities)
        if all_rules or entry.get('default') or (matches and not only_default):
            visit(entry['id'])
    return [entry for entry in data['entries'] if entry['id'] in chosen]


def detect(project):
    definitions = stack_definitions.load(LIBRARY)
    packages, stacks, databases, diagnostics = [], set(), set(), []
    state_path = safe(project, '.trellis/personal/install.json')
    preview = load(state_path).get('preview_scaffold') if state_path.is_file() else None
    excluded_preview = safe(project, preview) if preview else None
    for directory, children, files in os.walk(project, followlinks=False):
        children[:] = sorted(child for child in children if child not in IGNORED and
                             not (Path(directory) / child).is_symlink() and
                             (Path(directory) / child).resolve() != excluded_preview)
        for filename in sorted(files):
            path = Path(directory) / filename
            if not stack_facts.manifest_kind(path):
                continue
            text = stack_facts.bounded_text(path)
            if text is None:
                diagnostics.append(path.relative_to(project).as_posix() + ': linked/oversized/non-UTF8 manifest skipped')
                continue
            row = {'path': path.relative_to(project).as_posix(), 'stacks': [], 'versions': {}}
            stack_facts.inspect(project, path, text, row, definitions)
            # Unrelated Swift source is not a manifest or evidence for a SwiftUI application.
            if path.suffix == '.swift' and filename != 'Package.swift' and not row['stacks'] and not row['diagnostics']:
                continue
            stacks.update(row['stacks'])
            databases.update(row['databases'])
            diagnostics.extend(row['path'] + ': ' + message for message in row['diagnostics'])
            packages.append(row)
    all_stacks = stacks | databases
    return {'project': str(project), 'packages': packages, 'stacks': sorted(stacks),
            'databases': sorted(databases), 'capabilities': stack_definitions.capabilities(definitions, all_stacks),
            'database_route': stack_definitions.database_route(definitions, all_stacks), 'diagnostics': diagnostics,
            'definitions_sha256': digest((LIBRARY / 'stack-definitions.json').read_bytes()),
            'stack_state': 'detected' if all_stacks else 'undetermined',
            'preview_excluded_from_application_stack': preview}


def list_stacks(data=None):
    data = data or catalog()
    definitions = stack_definitions.load(LIBRARY)
    profiles = stack_registry(data)['profiles']
    known = {item['id'] for item in definitions['stacks']}
    if {profile['stack'] for profile in profiles} - known:
        raise ValueError('Source profile has no reviewed stack definition')
    groups = []
    for group in definitions['groups']:
        rows = []
        for definition in definitions['stacks']:
            if definition['group'] != group['id']:
                continue
            selected = [profile for profile in profiles if profile['stack'] == definition['id']]
            if not selected:
                raise ValueError('Stack definition has no source profile: ' + definition['id'])
            rows.append({**definition, 'profiles': selected,
                         'coverage_state': 'bundled_baseline' if any(profile['kind'] == 'personal' for profile in selected)
                         else 'official_acquisition', 'runtime_acceptance': 'not_certified_for_all_stacks'})
        groups.append({**group, 'count': len(rows), 'stacks': rows})
    return {'schema_version': 1, 'total_stacks': len(known), 'groups': groups,
            'definition_sha256': digest((LIBRARY / 'stack-definitions.json').read_bytes()),
            'registry_sha256': digest(json_bytes(stack_registry(data))),
            'scope': 'library coverage; acquisition, project adaptation and business runtime acceptance are separate'}


def stack_overview(coverage):
    lines = ['# 技术栈覆盖总览', '', '> 由 stack-definitions.json、catalog.json 和官方来源清单生成；修改源后运行 build。', '',
             '当前提供 **' + str(coverage['total_stacks']) + ' 个技术栈入口**。这里列出整个规范库，不是三个获取验收样例的范围。', '',
             'COMMON 是不绑定发布版本的工程基线：覆盖资源、模块、数据/交互和验证机制；不能当作所有版本 API 保证。',
             '版本专用规则只匹配登记的 major；React、Go、Rust保留固定提交/摘要的官方获取链路，离线需要已验证缓存。',
             '每个项目仍需 AI 阅读真实源码与官方对应版本，补项目规范并运行实际检查。规则/识别/复制消费通过不等于 53 种业务运行已验收。', '',
             '命令：`python3 scripts/personal.py list-stacks`（分组 JSON）；加 `--format markdown` 阅读中文表格。', '']
    for group in coverage['groups']:
        lines += ['## ' + group['title_zh'] + '（' + str(group['count']) + '）', '',
                  '| ID / 名称 | 具体覆盖 | 来源和版本边界 | 自动证据 / 缺口 |', '|---|---|---|---|']
        for row in group['stacks']:
            sources = []
            for profile in row['profiles']:
                if profile['kind'] == 'personal':
                    policy = 'COMMON' if profile.get('version_independent') else 'major ' + ','.join(map(str, profile['major_versions']))
                    sources.append('[' + profile['id'] + '](' + profile['source']['path'] + ')：' + policy)
                else:
                    policy = 'COMMON' if profile.get('version_independent') else 'major ' + ','.join(map(str, profile.get('major_versions', [])))
                    sources.append('[' + profile['id'] + '](' + profile['adaptation'] + ')：官方获取 ' + policy)
            route = ''
            if 'database' in row.get('capabilities', []):
                route = '；DBHub 候选，连接/运行待确认' if row.get('database_provider') else '；兼容 provider 待选择，不默认 DBHub'
            lines.append('| `' + row['id'] + '` / ' + row['name'] + ' | ' + row['summary_zh'] + ' | ' + '<br>'.join(sources) + ' | ' + row['detection_zh'] + route + ' |')
        lines.append('')
    lines += ['## 配置、边界与扩展', '',
              '- 识别定义使用 schema_version=1、groups/stacks、精确依赖 markers（kind/names/prefixes/version）及能力/provider 元数据。原生 index.json 保持独立。',
              '- 空白或动态配置项目可用 --stacks / --stack-versions 声明；原始配置与版本证据保留，冲突不覆盖实际事实。',
              '- 读取有字节上限，跳过 symlink/依赖/缓存目录和登记预览；不执行依赖、构建脚本、Docker 或下载资料中的命令。',
              '- packageManager/对应锁文件决定 npm/pnpm/yarn/bun 命令；没有配置时 npm 仅为待确认示例。pnpm 常见 importer、Yarn descriptor 与 npm 锁解析有范围，未支持格式保留声明/诊断。',
              '- Python 3.9/3.10 没有 tomli 时只支持静态单行 TOML；完整结构请使用 Python 3.11+ 或项目已有 tomli。Gradle alias/继承、复杂 YAML、CMake 动态语言等需显式声明/源码复核。',
              '- Java 1.8/VERSION_1_8 归一化为 8 并保留原值；Kotlin DSL 不等于 Kotlin 应用；C# LangVersion 与 .NET TFM/SDK 分开。',
              '- Dart 与 Flutter SDK、Swift 编译器与 tools-version/语言模式/SwiftUI SDK 分开；数据库驱动版本不当服务端版本，配置镜像只证明目标声明。',
              '- 新增栈：维护定义与具体规则/catalog 或官方 profile/适配指南，保留来源/覆盖/版本边界，再 build/validate 与独立消费。安装器复制这些元数据与 helper，保护本地改动。', '',
              '本轮保留的缺口：所有栈真实业务/设备/发布验证、未声明版本、动态/不支持清单、非 SQL provider，以及已有父任务的远程发布、客户端/模型/外部探索接入。', '']
    return ('\n'.join(lines)).encode()


def rule_index(entries):
    lines = ['# Personal development guidelines', '',
             'Read the current phase and target area only. Keep required architecture/design originals intact.', '',
             '| ID | Trigger / scope | Guideline |', '|---|---|---|']
    for entry in entries:
        relative = Path(entry['target']).relative_to('guides/personal')
        lines.append('| ' + entry['id'] + ' | ' + entry['summary'] + ' | [' +
                     entry['title'] + '](' + relative.as_posix() + ') |')
    return ('\n'.join(lines) + '\n').encode()


def category_indexes(entries):
    result = {}
    for category in ('core', 'process', 'engineering', 'stacks', 'tools'):
        chosen = [entry for entry in entries if entry['category'] == category]
        if not chosen:
            continue
        root = Path('guides/personal') / category
        lines = ['# ' + category.capitalize() + ' guidelines', '',
                 '## Pre-Development Checklist', '',
                 'Read only the applicable phase/package guidelines below. Project-local rules remain authoritative.', '',
                 '## Guidelines', '', '| ID | Scope | Guideline |', '|---|---|---|']
        for entry in chosen:
            target = Path(entry['target']).relative_to(root).as_posix()
            lines.append('| ' + entry['id'] + ' | ' + entry['summary'] + ' | [' + entry['title'] + '](' + target + ') |')
        lines += ['', '## Quality Check', '',
                  'Verify affected contracts and actual project commands. Preserve source/version and unresolved gaps.', '']
        result[(root / 'index.md').as_posix()] = '\n'.join(lines).encode()
    return result


def build():
    data = catalog()
    registry = stack_registry(data)
    stack_sources.validate_registry(json.loads(json_bytes(registry)), root=LIBRARY)
    coverage = list_stacks(data)
    write(LIBRARY / 'stack-sources.json', json_bytes(registry))
    write(LIBRARY / 'STACKS.zh-CN.md', stack_overview(coverage))
    entries = select(data, only_default=True)
    out = LIBRARY / 'bundles/personal-core'
    # Remove only generated files from the previous build, never source files.
    manifest_path = LIBRARY / 'bundles/personal-core.manifest.json'
    if manifest_path.exists():
        for item in load(manifest_path)['files']:
            previous = safe(out, item['path'])
            if previous.exists() and digest(previous.read_bytes()) != item['sha256']:
                raise ValueError('Generated bundle was locally edited: ' + item['path'])
            if previous.is_file():
                previous.unlink()
    contents = {entry['target']: safe(LIBRARY, entry['path']).read_bytes() for entry in entries}
    contents['guides/personal/index.md'] = rule_index(entries)
    contents.update(category_indexes(entries))
    records = []
    for relative, content in sorted(contents.items()):
        write(safe(out, relative), content)
        records.append({'path': relative, 'sha256': digest(content)})
    result = {'library_version': data['version'], 'rules': [entry['id'] for entry in entries], 'files': records,
              'source_hashes': {name: digest((LIBRARY / name).read_bytes()) for name in
                  ('catalog.json', 'stack-definitions.json', 'official-sources.lock.json', 'stack-sources.json', 'STACKS.zh-CN.md')}}
    write(manifest_path, json_bytes(result))
    return result


def stack_registry(data):
    profiles = []
    for entry in data['entries']:
        if entry['category'] != 'stacks':
            continue
        for stack in entry['stacks']:
            profiles.append({'id': entry['id'], 'kind': 'personal', 'stack': stack,
                             'major_versions': entry.get('major_versions', []),
                             'version_independent': entry.get('version_independent', False),
                             'source': {'path': entry['path'], 'sha256': digest(safe(LIBRARY, entry['path']).read_bytes())},
                             'license': 'personal draft; publication license pending',
                             'coverage': entry.get('coverage', ['project adaptation required']),
                             'baseline_kind': entry.get('baseline_kind', 'common' if entry.get('version_independent') else 'major_scoped'),
                             'source_ref': entry['source_ref'], 'reviewed_at': entry['retrieved_at']})
    profiles.extend(load(LIBRARY / 'official-sources.lock.json')['profiles'])
    return {'schema_version': 1, 'profiles': profiles}


def inventory(entries):
    result = {'.trellis/spec/' + entry['target']: safe(LIBRARY, entry['path']).read_bytes() for entry in entries}
    result['.trellis/spec/guides/personal/index.md'] = rule_index(entries)
    result.update({'.trellis/spec/' + path: content for path, content in category_indexes(entries).items()})
    for folder, target in [('skills', '.agents/skills'), ('templates', '.trellis/personal/templates')]:
        for source in sorted((LIBRARY / folder).rglob('*')):
            if source.is_file():
                result[target + '/' + source.relative_to(LIBRARY / folder).as_posix()] = source.read_bytes()
    # Ship the source library and executable helper independently of Trellis spec downloads.
    for name in ['catalog.json', 'index.json', 'library.json', 'tools.lock.json', 'stack-sources.json', 'stack-definitions.json', 'STACKS.zh-CN.md', 'official-sources.lock.json', 'README.md', 'CHANGELOG.md', 'DISTRIBUTION.zh-CN.md', 'THIRD_PARTY_NOTICES.md', 'release-policy.json', '.gitignore']:
        source = LIBRARY / name
        if source.exists():
            result['.trellis/personal/library/' + name] = source.read_bytes()
    for folder in ['specs', 'templates', 'skills', 'scripts', 'adapters', 'workflows', 'bundles', 'apps', 'examples']:
        for source in sorted((LIBRARY / folder).rglob('*')):
            if source.is_file() and not set(source.relative_to(LIBRARY).parts) & {'__pycache__', 'node_modules', 'dist', '.git'} and source.suffix != '.pyc':
                result['.trellis/personal/library/' + source.relative_to(LIBRARY).as_posix()] = source.read_bytes()
    result['.trellis/workflow.md'] = (LIBRARY / 'workflows/chinese-design-first.md').read_bytes()
    result['.trellis/personal/personal.py'] = (
        'from pathlib import Path\nimport runpy\n'
        "runpy.run_path(str(Path(__file__).parent / 'library/scripts/personal.py'), run_name='__main__')\n"
    ).encode()
    result['.trellis/personal/.gitignore'] = (
        '# Local runtime, credentials and evidence; distributable assets remain versioned.\n'
        'backups/\ncache/\ntools/\nevidence/\nprivate/\nconfig-candidates/\n'
        '*-state.json\n*-report.json\ninstall.json\n'
    ).encode()
    result['.qmd/.gitignore'] = '*\n!.gitignore\n'.encode()
    result['.codegraph/.gitignore'] = '*\n!.gitignore\n'.encode()
    return result


def query_stacks(project, stacks=None, versions=None, registry=None, offline=False):
    data = catalog()
    detected = detect(project)
    state = safe(project, '.trellis/personal/install.json')
    previous = load(state) if state.is_file() else {}
    stacks = stacks if stacks is not None else previous.get('declared_stacks', [])
    versions = versions if versions is not None else previous.get('stack_versions', {})
    registry = registry or previous.get('stack_registry')
    selected = sorted(set(stacks) | set(versions) | set(detected['stacks']) | set(detected['databases']))
    io = SimpleNamespace(safe=safe, write=write)
    return stack_sources.resolve(project, LIBRARY, data, detected, selected, versions or {}, registry, offline, io)


def install(project, stacks=None, capabilities=None, adopt_workflow=False, preview_scaffold=None,
            stack_versions=None, stack_registry=None, offline=False):
    data = catalog()
    detected = detect(project)
    state_path = safe(project, '.trellis/personal/install.json')
    previous = load(state_path) if state_path.exists() else {'files': {}}
    declared_stacks = list(stacks) if stacks is not None else previous.get('declared_stacks', [])
    declared_capabilities = list(capabilities) if capabilities is not None else previous.get('declared_capabilities', [])
    stacks = sorted(set(declared_stacks) | set(detected['stacks']) | set(detected['databases']))
    definitions = stack_definitions.load(LIBRARY)
    capabilities = sorted(set(declared_capabilities) | set(stack_definitions.capabilities(definitions, stacks)))
    stack_registry = stack_registry or previous.get('stack_registry')
    stack_versions = stack_versions if stack_versions is not None else previous.get('stack_versions', {})
    stacks = sorted(set(stacks) | set(stack_versions))
    capabilities = sorted(set(capabilities) | set(stack_definitions.capabilities(definitions, stacks)))
    database_route = stack_definitions.database_route(definitions, stacks, 'database' in capabilities)
    entries = select(data, stacks, capabilities)
    source_report, source_assets, source_entries = stack_sources.resolve(
        project, LIBRARY, data, detected, stacks, stack_versions, stack_registry, offline,
        SimpleNamespace(safe=safe, write=write))
    # A transient source failure must not erase the last acquired project rule.
    source_guards = set()
    source_record = safe(project, '.trellis/personal/spec-sources.json')
    prior_sources = load(source_record).get('packages', []) if source_record.is_file() else []
    prior_sources = {row['target']: row for row in prior_sources}
    for row in source_report['packages']:
        prior = prior_sources.get(row['target'])
        active_profile = prior.get('active_profile_id', prior.get('profile_id')) if prior else None
        active_source = prior.get('active_source', prior.get('source')) if prior else None
        failed_prior = prior and any(attempt['profile_id'] == active_profile and
                                     attempt['state'] == 'acquisition_failed' for attempt in row['attempts'])
        if (prior and active_source and row['target'] in previous['files'] and
                (row['status'] != 'acquired' or failed_prior and row.get('profile_id') != active_profile)):
            source_guards.add(row['target'])
            row['adoption_state'] = 'preserved_previous_rule'
            row['previous_profile_id'] = active_profile
            row['active_profile_id'], row['active_source'] = active_profile, active_source
            row['candidate'] = row['target'] + '.new.' + digest(source_assets[row['target']])[:12]
    # Different majors use distinct rules; unknown versions cannot choose between major-specific profiles.
    entries = [entry for entry in entries if entry['category'] != 'stacks' or any(
        facts['stack'] in entry['stacks'] and (facts.get('bundled_rule_id') == entry['id'] or
            facts['status'] == 'version_unconfirmed' and stack_sources.compatible(entry, facts['version']) is None and
            sum(facts['stack'] in candidate.get('stacks', []) for candidate in data['entries'] if candidate['category'] == 'stacks') == 1)
        for facts in source_report['packages'])]
    revision = stamp()
    changes, actions, known, pending = [], [], dict(previous['files']), []
    marker_start, marker_end = '<!-- PERSONAL_TRELLIS:START -->', '<!-- PERSONAL_TRELLIS:END -->'
    agents = safe(project, 'AGENTS.md')
    before = agents.read_bytes() if agents.exists() else None
    body = before.decode() if before else ''
    section = marker_start + '\n## Personal workflow\nRead `.trellis/spec/guides/personal/index.md` for the current phase and target area.\nUse `.agents/skills/personal-project-init`, `personal-project-explore`, and `personal-design` when their triggers apply.\n' + marker_end
    managed_block = False
    if marker_start in body:
        if marker_end not in body or body.count(marker_start) != 1 or body.count(marker_end) != 1:
            raise ValueError('Ambiguous personal AGENTS block; preserve and repair explicitly')
        pattern = re.escape(marker_start) + '.*?' + re.escape(marker_end)
        existing = re.search(pattern, body, re.S).group(0)
        managed_block = digest(existing.encode()) == previous.get('agents_block_sha256')
        body = re.sub(pattern, lambda _: section, body, flags=re.S)
    else:
        body = body.rstrip() + ('\n\n' if body.strip() else '') + section + '\n'
        managed_block = True
    assets = inventory(entries)
    assets.update(source_assets)
    index_entries = entries + source_entries
    assets['.trellis/spec/guides/personal/index.md'] = rule_index(index_entries)
    assets.update({'.trellis/spec/' + path: content for path, content in category_indexes(index_entries).items()})
    assets['.trellis/personal/spec-sources.json'] = json_bytes(source_report)
    assets['.trellis/personal/spec-sources.zh-CN.md'] = stack_sources.chinese_report(source_report)
    if preview_scaffold:
        safe(project, preview_scaffold)
        for source in sorted((LIBRARY / 'apps/design-preview').rglob('*')):
            relative = source.relative_to(LIBRARY / 'apps/design-preview')
            if source.is_file() and not set(relative.parts) & {'node_modules', 'dist', '.git', '.cache'}:
                assets[Path(preview_scaffold).joinpath(relative).as_posix()] = source.read_bytes()
    assets['AGENTS.md'] = body.encode()
    # Resolve every destination and conflict before changing the consumer.
    for relative, content in assets.items():
        destination = safe(project, relative)
        if destination.exists() and not destination.is_file():
            raise ValueError('Destination is not a file: ' + relative)
        old = destination.read_bytes() if destination.exists() else None
        old_hash = digest(old) if old is not None else None
        source_hash = digest(content)
        tracked = previous['files'].get(relative)
        unchanged = tracked and tracked['installed_sha256'] == old_hash
        explicit_workflow = relative == '.trellis/workflow.md' and adopt_workflow
        explicit_block = relative == 'AGENTS.md' and managed_block
        if old_hash == source_hash:
            action = 'reused'
        elif relative not in source_guards and (old is None or unchanged or explicit_workflow or explicit_block):
            changes.append({'path': relative, 'before': base64.b64encode(old).decode() if old is not None else None,
                            'after_sha256': source_hash})
            pending.append((destination, content))
            action = 'installed' if old is None else 'updated'
        else:
            candidate = relative + '.new.' + source_hash[:12]
            sidecar = safe(project, candidate)
            if sidecar.exists() and (not sidecar.is_file() or sidecar.read_bytes() != content):
                raise ValueError('Candidate was independently modified: ' + candidate)
            if not sidecar.exists():
                changes.append({'path': candidate, 'before': None, 'after_sha256': source_hash})
            pending.append((sidecar, content))
            actions.append({'path': relative, 'action': 'conflict', 'candidate': candidate})
            continue
        known[relative] = {'installed_sha256': source_hash, 'library_version': data['version']}
        actions.append({'path': relative, 'action': action})
    report = {'revision': revision, 'library_version': data['version'], 'detected': detected,
              'stack_registry': stack_registry, 'stack_versions': stack_versions,
              'declared_stacks': declared_stacks, 'declared_capabilities': declared_capabilities,
              'spec_sources_state': source_report['state'],
              'spec_sources_report': '.trellis/personal/spec-sources.zh-CN.md',
              'spec_adaptation': source_report['adaptation_state'],
              'spec_adoption_conflicts': sorted(source_guards),
              'preview_scaffold': preview_scaffold or previous.get('preview_scaffold'),
              'selected_stacks': stacks, 'selected_capabilities': capabilities, 'database_route': database_route,
              'unmatched_stacks': sorted({row['stack'] for row in source_report['packages'] if row['status'] != 'acquired'}),
              'unmatched_catalog_stacks': sorted(set(stacks) - {stack for entry in data['entries'] for stack in entry.get('stacks', [])}),
              'project_rules': [{'id': entry['id'], 'target': '.trellis/spec/' + entry['target']} for entry in source_entries],
              'rules': [entry['id'] for entry in entries], 'actions': actions,
              'status': 'conflicts' if any(row['action'] == 'conflict' for row in actions) else 'installed',
              'tools': 'not_verified_by_asset_install', 'files': known,
              'agents_block_sha256': previous.get('agents_block_sha256') if
              any(row['path'] == 'AGENTS.md' and row['action'] == 'conflict' for row in actions) else digest(section.encode())}
    backup = {'revision': revision, 'changes': changes,
              'previous_state': base64.b64encode(state_path.read_bytes()).decode() if state_path.exists() else None}
    write(safe(project, '.trellis/personal/backups/' + revision + '.json'), json_bytes(backup))
    write(state_path, json_bytes({**report, 'status': 'installing'}))
    for destination, content in pending:
        write(destination, content)
    write(state_path, json_bytes(report))
    return report


def rollback(project, revision):
    record = load(safe(project, '.trellis/personal/backups/' + revision + '.json'))
    conflicts = []
    for row in reversed(record['changes']):
        destination = safe(project, row['path'])
        current = destination.read_bytes() if destination.exists() else None
        before = base64.b64decode(row['before']) if row['before'] is not None else None
        if current == before:
            continue
        if current is None or digest(current) != row['after_sha256']:
            conflicts.append(row['path'])
            continue
        if row['before'] is None:
            destination.unlink()
        else:
            write(destination, before)
    if not conflicts:
        state = safe(project, '.trellis/personal/install.json')
        if record['previous_state'] is None:
            state.unlink(missing_ok=True)
        else:
            write(state, base64.b64decode(record['previous_state']))
    return {'revision': revision, 'status': 'conflicts' if conflicts else 'rolled_back', 'conflicts': conflicts}


def validate():
    data = catalog()
    if load(LIBRARY / 'stack-sources.json') != stack_registry(data):
        raise ValueError('Stale generated stack registry; run build')
    stack_sources.validate_registry(load(LIBRARY / 'stack-sources.json'), root=LIBRARY)
    coverage = list_stacks(data)
    if (LIBRARY / 'STACKS.zh-CN.md').read_bytes() != stack_overview(coverage):
        raise ValueError('Stale generated coverage overview; run build')
    for profile in load(LIBRARY / 'stack-sources.json')['profiles']:
        if profile.get('adaptation'):
            stack_sources.read_local(LIBRARY, profile['adaptation'])
    # Walk every dependency closure, including optional rules.
    select(data, all_rules=True)
    missing = []
    documents = [file for name in ('specs', 'templates', 'skills', 'workflows')
                 for file in (LIBRARY / name).rglob('*.md')] + [LIBRARY / 'STACKS.zh-CN.md', LIBRARY / 'README.md']
    for file in documents:
        body = file.read_text(encoding='utf-8')
        if not body.endswith('\n') or body.count('```') % 2:
            raise ValueError('Malformed Markdown: ' + str(file.relative_to(LIBRARY)))
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', body):
            target = target.split('#')[0].strip('<>')
            if target and not re.match(r'[a-z]+:', target) and not (file.parent / target).resolve().exists():
                missing.append({'file': str(file.relative_to(LIBRARY)), 'target': target})
    index = load(LIBRARY / 'index.json')
    if index['version'] != 1:
        raise ValueError('Unsupported native marketplace version')
    for entry in index['templates']:
        path = safe(LIBRARY, entry['path'])
        if not path.exists() or entry['type'] not in {'spec', 'workflow'}:
            raise ValueError('Invalid native marketplace entry')
    bundle = load(LIBRARY / 'bundles/personal-core.manifest.json')
    for name, expected in bundle.get('source_hashes', {}).items():
        if digest(safe(LIBRARY, name).read_bytes()) != expected:
            raise ValueError('Stale bundle source hash: ' + name)
    if bundle['rules'] != [entry['id'] for entry in select(data, only_default=True)]:
        raise ValueError('Stale bundle selection; run build')
    default_entries = select(data, only_default=True)
    expected_contents = {entry['target']: safe(LIBRARY, entry['path']).read_bytes() for entry in default_entries}
    expected_contents['guides/personal/index.md'] = rule_index(default_entries)
    expected_contents.update(category_indexes(default_entries))
    if {row['path']: row['sha256'] for row in bundle['files']} != {
            path: digest(content) for path, content in expected_contents.items()}:
        raise ValueError('Stale generated bundle source; run build')
    for row in bundle['files']:
        if digest(safe(LIBRARY / 'bundles/personal-core', row['path']).read_bytes()) != row['sha256']:
            raise ValueError('Stale generated bundle: ' + row['path'])
    if missing:
        raise ValueError('Broken local links: ' + json.dumps(missing))
    return {'status': 'passed', 'rules': len(data['entries']), 'markdown_files': len(documents),
            'native_templates': len(index['templates']), 'missing_links': missing, 'stack_ids': coverage['total_stacks']}


def verify_design(project, relative, allow_draft=False):
    manifest = load(safe(project, relative))
    documents = {row['id']: row for row in manifest['documents']}
    failures = []
    if len(documents) != len(manifest['documents']) or not manifest['features']:
        failures.append('duplicate document IDs or empty feature scope')
    if len({feature['id'] for feature in manifest['features']}) != len(manifest['features']):
        failures.append('duplicate feature IDs')
    for row in documents.values():
        file = safe(project, row['path'])
        if not file.exists():
            failures.append('missing document: ' + row['id'])
        elif not file.is_file() or not row.get('version'):
            failures.append('invalid document/version: ' + row['id'])
        elif not allow_draft and digest(file.read_bytes()) != row.get('approved_sha256'):
            failures.append('unapproved or changed document: ' + row['id'])
    for feature in manifest['features']:
        if not feature.get('acceptance'):
            failures.append('missing acceptance: ' + feature['id'])
        for kind in ['prd', 'tdd'] + ([] if feature.get('ui_applicable') is False else ['ui']):
            reference = feature.get(kind)
            if reference not in documents:
                failures.append('missing ' + kind + ' mapping: ' + feature['id'])
        for artifact in feature.get('artifacts', []):
            file = safe(project, artifact['path'])
            if not file.exists():
                failures.append('missing artifact: ' + artifact['path'])
            elif not allow_draft and digest(file.read_bytes()) != artifact.get('sha256'):
                failures.append('stale artifact: ' + artifact['path'])
            source = documents.get(artifact.get('source_document'))
            if not source or artifact.get('source_sha256') != source.get('approved_sha256'):
                failures.append('missing/stale artifact source: ' + artifact['path'])
    if not allow_draft and not manifest.get('confirmation', {}).get('reference'):
        failures.append('missing user confirmation evidence')
    return {'status': 'failed' if failures else 'passed', 'features': len(manifest['features']),
            'failures': failures, 'semantic_and_user_acceptance': 'requires_review'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'validate', 'detect', 'list-stacks', 'query-stacks', 'install', 'rollback', 'verify-design'])
    parser.add_argument('--format', choices=['json', 'markdown'], default='json', help='list-stacks output format')
    parser.add_argument('--project', type=Path, default=Path.cwd())
    parser.add_argument('--stacks', nargs='*', default=None)
    parser.add_argument('--capabilities', nargs='*', default=None)
    parser.add_argument('--adopt-workflow', action='store_true', help='Back up and explicitly replace current workflow')
    parser.add_argument('--preview-scaffold', help='Copy the extensible Storybook preview to this project-relative directory')
    parser.add_argument('--revision')
    parser.add_argument('--manifest', default='.trellis/personal/design-manifest.json')
    parser.add_argument('--allow-draft', action='store_true')
    parser.add_argument('--stack-versions', nargs='*', default=None, metavar='STACK=VERSION',
                        help='Declare confirmed target versions; never override conflicting package facts')
    parser.add_argument('--stack-registry', help='Local stack-sources.json or gh:OWNER/REPO[/subdir]#FULL_COMMIT_SHA')
    parser.add_argument('--offline', action='store_true', help='Use bundled rules and hash-verified source cache only')
    args = parser.parse_args()
    project = args.project.resolve()
    versions = None
    if args.stack_versions is not None:
        versions = {}
        for item in args.stack_versions:
            key, separator, value = item.partition('=')
            if not separator or not value or key in versions:
                parser.error('--stack-versions requires distinct STACK=VERSION values')
            versions[key] = value
    if args.command == 'build':
        result = build()
    elif args.command == 'validate':
        result = validate()
    elif args.command == 'list-stacks':
        result = list_stacks()
        if args.format == 'markdown':
            print(stack_overview(result).decode(), end='')
            return 0
    elif args.command == 'detect':
        result = detect(project)
    elif args.command == 'query-stacks':
        result, _, _ = query_stacks(project, args.stacks, versions, args.stack_registry, args.offline)
    elif args.command == 'install':
        project.mkdir(parents=True, exist_ok=True)
        result = install(project, args.stacks, args.capabilities, args.adopt_workflow, args.preview_scaffold,
                         versions, args.stack_registry, args.offline)
        result = {key: value for key, value in result.items() if key not in {'files', 'actions'}} | {
            'action_counts': {action: sum(row['action'] == action for row in result['actions'])
                              for action in ['installed', 'updated', 'reused', 'conflict']}}
    elif args.command == 'rollback':
        if not args.revision:
            parser.error('rollback requires --revision')
        result = rollback(project, args.revision)
    else:
        result = verify_design(project, args.manifest, args.allow_draft)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if (result.get('status') in {'failed', 'conflicts'} or result.get('state') in {'incomplete', 'stack_undetermined'}
                 or result.get('spec_sources_state') in {'incomplete', 'stack_undetermined'}) else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        print(json.dumps({'status': 'failed', 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
