"""Bounded local manifest evidence; never execute discovered commands/dependencies."""
import ast
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import stack_definitions
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None
LIMIT = 1_000_000
QUOTED = r'''"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:\\.|[^"\\\n\r])*"|'(?:\\.|[^'\\\n\r])*' '''.strip()


def bounded_text(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > LIMIT:
        return None
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeError:
        return None


def manifest_kind(path):
    names = {'package.json': 'npm', 'pom.xml': 'maven', 'build.gradle': 'gradle',
             'build.gradle.kts': 'gradle', 'pyproject.toml': 'python', 'requirements.txt': 'python',
             'go.mod': 'go', 'Cargo.toml': 'cargo', 'composer.json': 'composer',
             'pubspec.yaml': 'pub', 'Package.swift': 'swift', 'project.pbxproj': 'xcode',
             'CMakeLists.txt': 'cmake', 'project.config.json': 'wechat', 'global.json': 'dotnet',
             'Dockerfile': 'docker', 'compose.yml': 'docker', 'compose.yaml': 'docker',
             'docker-compose.yml': 'docker', 'docker-compose.yaml': 'docker'}
    if path.name in names:
        return names[path.name]
    return 'nuget' if path.suffix == '.csproj' else 'swift-source' if path.suffix == '.swift' else None


def java_version(raw):
    value = raw.strip()
    match = re.fullmatch(r'(?:JavaVersion\.)?VERSION_(\d+)(?:_(\d+))?', value)
    if match:
        return match.group(2) if match.group(1) == '1' and match.group(2) else match.group(1)
    return value[2:] if re.fullmatch(r'1\.\d+', value) else value


def without_code_comments(text):
    """Keep quoted configuration values intact while removing line/block comments."""
    tokens = QUOTED + r'|//[^\n]*|/\*[\s\S]*?\*/'
    return re.sub(tokens, lambda match: re.sub(r'[^\n]', ' ', match.group())
                  if match.group().startswith(('//', '/*')) else match.group(), text)


def code_matches(pattern, text):
    """Match static calls outside quoted documentation/example values."""
    for match in re.finditer(pattern + '|' + QUOTED, text):
        if match.group(1) is not None:
            yield match.groups()


def nearby(project, directory, name):
    while directory == project or project in directory.parents:
        path = directory / name
        # No ancestor of an auxiliary file may be a symlink.
        linked = any(parent.is_symlink() for parent in (path, *path.parents) if parent == project or project in parent.parents)
        text = None if linked else bounded_text(path)
        if text is not None:
            return path, text
        if directory == project:
            break
        directory = directory.parent
    return None, None


def toml_data(text, row):
    if tomllib:
        return tomllib.loads(text)
    row['diagnostics'].append('Full TOML unavailable; only static single-line fields parsed; use tomli or Python 3.11+')
    data, table = {}, {}
    for line in text.splitlines():
        match = re.match(r'^\s*\[([\w.-]+)\]\s*$', line)
        if match:
            table = data
            for part in match.group(1).split('.'):
                table = table.setdefault(part, {})
        match = re.match(r"^\s*([\w-]+)\s*=\s*([\"'].*[\"']|\[.*\])\s*$", line)
        if match:
            try:
                table[match.group(1)] = ast.literal_eval(match.group(2))
            except (ValueError, SyntaxError):
                pass
    return data


def npm_facts(project, path, text, row, add):
    manifest = json.loads(text)
    if not isinstance(manifest, dict) or any(not isinstance(manifest.get(key, {}), dict)
            for key in ('dependencies', 'devDependencies', 'peerDependencies', 'scripts', 'engines')):
        raise ValueError('Invalid package.json object fields: ' + row['path'])
    deps = {**manifest.get('peerDependencies', {}), **manifest.get('devDependencies', {}), **manifest.get('dependencies', {})}
    if any(not isinstance(value, str) for value in deps.values()):
        raise ValueError('Dependency versions must be strings: ' + row['path'])
    add('feature', 'javascript')
    for name, value in deps.items():
        add('npm', name, value, row['path'] + ': declared dependency ' + name)
    if manifest.get('engines', {}).get('node'):
        add('feature', 'node', manifest['engines']['node'], row['path'] + ': engines.node')
    for name in ('.nvmrc', '.node-version'):
        runtime, value = nearby(project, path.parent, name)
        if value and re.fullmatch(r'v?\d+(?:\.\d+){0,2}\s*', value):
            add('feature', 'node', value.strip().lstrip('v'), runtime.relative_to(project).as_posix())
    manager = manifest.get('packageManager')
    if manager is not None and not isinstance(manager, str):
        raise ValueError('packageManager must be a string')
    if not manager:
        owner = path.parent.parent
        while owner == project or project in owner.parents:
            value = bounded_text(owner / 'package.json')
            if value:
                parent = json.loads(value)
                if isinstance(parent, dict) and parent.get('packageManager'):
                    manager = parent['packageManager']
                    row['runner_evidence'] = (owner / 'package.json').relative_to(project).as_posix() + ': packageManager'
                    break
            if owner == project:
                break
            owner = owner.parent
    locks = {name: nearby(project, path.parent, file) for name, file in
             [('npm', 'package-lock.json'), ('pnpm', 'pnpm-lock.yaml'), ('yarn', 'yarn.lock'), ('bun', 'bun.lock')]}
    available = [name for name, (lock, _) in locks.items() if lock]
    if available:
        distance = {name: len(path.parent.relative_to(locks[name][0].parent).parts) for name in available}
        nearest = min(distance.values())
        nearest_available = [name for name in available if distance[name] == nearest]
    else:
        nearest_available = []
    declared = manager.split('@', 1)[0] if isinstance(manager, str) else None
    if declared and declared not in locks:
        row['diagnostics'].append('Unrecognized packageManager; select actual validation runner')
        runner = None
    elif declared:
        runner = declared
        row.setdefault('runner_evidence', row['path'] + ': packageManager')
    elif len(nearest_available) == 1:
        runner = nearest_available[0]
        row['runner_evidence'] = locks[runner][0].relative_to(project).as_posix()
    elif not available:
        runner = 'npm'
        row['runner_evidence'] = 'npm example only; no packageManager/lock evidence'
        row['diagnostics'].append('No packageManager/lock evidence; npm script command is a proposed entry pending runner review')
    else:
        runner = None
        row['diagnostics'].append('Conflicting lockfile runners; select the actual project runner')
    row['package_manager'] = runner
    if declared and any(name != declared for name in available):
        row['diagnostics'].append('Other runner lockfile present; only declared packageManager used')
    for name, value in manifest.get('scripts', {}).items():
        if not isinstance(value, str):
            raise ValueError('Configured scripts must be strings')
        if runner and name in {'lint', 'typecheck', 'type-check', 'test', 'build', 'check'}:
            row['commands'].append(runner + ' run ' + name)
    if not runner or not locks[runner][0]:
        return
    lock, lock_text = locks[runner]
    origin = lock.relative_to(project).as_posix() + ': resolved dependency '
    resolved = {}
    try:
        if runner == 'npm':
            data = json.loads(lock_text)
            entries = data.get('packages', {})
            prefix = path.parent.relative_to(lock.parent).as_posix()
            for name in deps:
                record = entries.get((prefix + '/' if prefix != '.' else '') + 'node_modules/' + name,
                                     entries.get('node_modules/' + name, {}))
                if not record and prefix == '.':
                    record = data.get('dependencies', {}).get(name, {})
                if isinstance(record, dict) and record.get('version'):
                    resolved[name] = record['version']
        elif runner == 'pnpm':
            scope = path.parent.relative_to(lock.parent).as_posix()
            importer, section, dependency = None, None, None
            for line in lock_text.splitlines():
                match = re.match(r'^  ([^ ].*):\s*$', line)
                if match:
                    importer, section, dependency = match.group(1).strip("\"'"), None, None
                match = re.match(r'^    (dependencies|devDependencies|optionalDependencies):\s*$', line)
                if match:
                    section = match.group(1)
                match = re.match(r'^      (.+):\s*$', line)
                if match:
                    dependency = match.group(1).strip("\"'")
                match = re.match(r"^        version:\s*[\"']?([^\s\"']+)", line)
                if match and importer == scope and section and dependency in deps:
                    resolved[dependency] = match.group(1).split('(', 1)[0]
            if not resolved:
                row['diagnostics'].append('pnpm importer version shape unsupported/missing; declarations retained')
        elif runner == 'yarn':
            for block in re.split(r'\n(?=\S)', lock_text):
                header = block.splitlines()[0] if block.splitlines() else ''
                version = re.search(r"^\s+version(?::|\s)\s*[\"']?([^\s\"']+)", block, re.M)
                if not version:
                    continue
                descriptors = header.rstrip(':').replace('"', '').split(', ')
                for name, constraint in deps.items():
                    if name + '@' + constraint in descriptors or name + '@npm:' + constraint in descriptors:
                        resolved[name] = version.group(1)
        else:
            row['diagnostics'].append('Bun resolved lock format not parsed; declarations retained')
        for name, value in resolved.items():
            if re.fullmatch(r'\d+(?:\.\d+){1,2}(?:-[\w.-]+)?', str(value)):
                add('npm', name, value, origin + name)
    except (ValueError, AttributeError, TypeError):
        row['diagnostics'].append('Lockfile unparseable; declarations retained')


def python_requirement(value, origin, add):
    match = re.match(r'^\s*([A-Za-z0-9][\w.-]*)(?:\[[^\]]+\])?\s*([^;#]*)', value)
    if match:
        name = re.sub(r'[-_.]+', '-', match.group(1)).lower()
        constraint = match.group(2).strip()
        if constraint.startswith('(') and constraint.endswith(')'):
            constraint = constraint[1:-1]
        add('python', name, constraint or None, origin + ': dependency ' + name)


def inspect(project, path, text, row, definitions):
    row.update(scope=path.parent.relative_to(project).as_posix(), version_evidence={}, commands=[],
               diagnostics=[], language_modes={}, tool_versions={})
    facts = []
    def add(kind, name, value=None, origin=None, raw=None):
        if kind == 'nuget':
            name = name.lower()
        facts.append({'kind': kind, 'name': name, 'version': value if isinstance(value, str) else None,
                      'origin': origin or row['path'] + ': ' + name, 'raw': raw or value})
    kind = manifest_kind(path)
    try:
        if kind == 'npm':
            npm_facts(project, path, text, row, add)
        elif kind == 'maven':
            root = ET.fromstring(text)
            local = lambda tag: tag.rsplit('}', 1)[-1]
            if local(root.tag) != 'project':
                raise ValueError('Maven root must be project')
            props = {local(child.tag): (child.text or '').strip() for parent in root.iter()
                     if local(parent.tag) == 'properties' for child in parent}
            def expand(value):
                for _ in range(5):
                    revised = re.sub(r'\$\{([^}]+)\}', lambda match: props.get(match.group(1), match.group(0)), value or '')
                    if revised == value:
                        return revised
                    value = revised
                return value
            add('feature', 'maven')
            add('feature', 'java')
            for key in ('maven.compiler.release', 'java.version', 'maven.compiler.source'):
                if props.get(key):
                    raw = expand(props[key])
                    add('feature', 'java', java_version(raw), row['path'] + ': ' + key, raw)
                    break
            for parent in root.iter():
                if local(parent.tag) not in {'dependency', 'plugin', 'parent'}:
                    continue
                children = {local(child.tag): (child.text or '').strip() for child in parent}
                if children.get('groupId') and children.get('artifactId'):
                    name = children['groupId'] + ':' + children['artifactId']
                    add('maven', name, expand(children.get('version')), row['path'] + ': ' + local(parent.tag) + ' ' + name)
            row['commands'] = ['mvn -f ' + row['path'] + ' verify (confirm reactor root and selected modules)']
        elif kind == 'gradle':
            code = without_code_comments(text)
            wrapper, value = nearby(project, path.parent, 'gradle/wrapper/gradle-wrapper.properties')
            version = re.search(r'gradle-([0-9]+(?:\.[0-9]+)+)-(?:bin|all)\.zip', value or '')
            add('feature', 'gradle', version.group(1) if version else None,
                wrapper.relative_to(project).as_posix() if version else None)
            for plugin, version in code_matches(r"\bid\s*(?:\(\s*)?[\"']([^\"']+)[\"']\s*\)?\s*(?:version\s*[\"']([^\"']+)[\"'])?", code):
                add('gradle-plugin', plugin, version or None)
            for target, version in code_matches(r"\bkotlin\s*\(\s*[\"'](jvm|android|multiplatform)[\"']\s*\)\s*(?:version\s*[\"']([^\"']+)[\"'])?", code):
                add('gradle-plugin', 'org.jetbrains.kotlin.' + target, version or None)
            if re.search(r'^\s*(?:`java-library`|java)\s*$', code, re.M):
                add('gradle-plugin', 'java')
            match = re.search(r"JavaLanguageVersion\.of\(\s*(\d+)\s*\)|(?:JavaVersion\.)?(VERSION_\d+(?:_\d+)?)|sourceCompatibility\s*=\s*[\"'](1\.\d+|\d+)[\"']", code)
            if match:
                raw = next(value for value in match.groups() if value)
                add('feature', 'java', java_version(raw), row['path'] + ': Java toolchain/sourceCompatibility', raw)
            configurations = r'implementation|api|compileOnly|runtimeOnly|testImplementation|testRuntimeOnly|testCompileOnly|annotationProcessor|classpath|kapt|ksp|compile|runtime|testCompile|testRuntime'
            notation = r"\b(?:" + configurations + r")\s*(?:\(\s*)?(?:(?:platform|enforcedPlatform)\s*\(\s*)?[\"']([\w.-]+:[\w.-]+):([^\"']+)[\"']"
            for name, version in code_matches(notation, code):
                add('gradle', name, version)
            row['diagnostics'].append('Gradle only static dependency call notation parsed; custom configurations/map notation/dynamic values require source review')
            if 'libs.' in code:
                row['diagnostics'].append('Gradle version catalog aliases require source review/explicit declaration')
            wrapper, _ = nearby(project, path.parent, 'gradlew')
            if wrapper:
                row['commands'] = ['./gradlew check (from ' + wrapper.parent.relative_to(project).as_posix() + '; confirm multi-module scope)']
        elif kind == 'python':
            add('feature', 'python')
            if path.name == 'pyproject.toml':
                data = toml_data(text, row)
                config = data.get('project', {})
                add('feature', 'python', config.get('requires-python'), row['path'] + ': requires-python')
                deps = list(config.get('dependencies', []))
                for values in config.get('optional-dependencies', {}).values():
                    deps += values
                for dep in deps:
                    python_requirement(dep, row['path'], add)
                poetry = data.get('tool', {}).get('poetry', {})
                groups = [poetry.get('dependencies', {})] + [group.get('dependencies', {}) for group in poetry.get('group', {}).values()]
                for deps in groups:
                    for name, value in deps.items():
                        version = value.get('version') if isinstance(value, dict) else value
                        if name == 'python':
                            add('feature', 'python', version, row['path'] + ': Poetry Python constraint')
                        else:
                            python_requirement(name + ' ' + (version or ''), row['path'], add)
                if 'pytest' in data.get('tool', {}):
                    row['commands'].append('python -m pytest (confirm project interpreter and environment)')
            else:
                for line in text.splitlines():
                    if line.strip().startswith(('-r', '-c', '--', '-e')):
                        row['diagnostics'].append('Requirements include/options/editable entry not followed; review owner')
                    elif line.strip() and not line.lstrip().startswith('#'):
                        python_requirement(line, row['path'], add)
            runtime = path.parent / '.python-version'
            value = bounded_text(runtime)
            if value and re.fullmatch(r'\d+\.\d+(?:\.\d+)?\s*', value):
                add('feature', 'python', value.strip(), runtime.relative_to(project).as_posix())
            if bounded_text(path.parent / 'pytest.ini') is not None:
                row['commands'].append('python -m pytest (confirm project interpreter and environment)')
        elif kind == 'go':
            match = re.search(r'^go\s+(\d+\.\d+(?:\.\d+)?)\s*$', text, re.M)
            add('feature', 'go', match.group(1) if match else None, row['path'] + ': go directive')
            for name, version in re.findall(r'^\s*(?:require\s+)?([\w./-]+)\s+(v\d+[^\s]*)', text, re.M):
                add('go', name, version.lstrip('v'))
            row['commands'] = ['go test ./... (from ' + row['scope'] + ')']
        elif kind == 'cargo':
            data = toml_data(text, row)
            add('feature', 'rust', data.get('package', {}).get('rust-version'), row['path'] + ': rust-version')
            for section in ('dependencies', 'dev-dependencies', 'build-dependencies'):
                for name, value in data.get(section, {}).items():
                    add('cargo', value.get('package', name) if isinstance(value, dict) else name,
                        value.get('version') if isinstance(value, dict) else value)
            row['commands'] = ['cargo test (from ' + row['scope'] + '; confirm workspace/package selection)']
        elif kind == 'composer':
            data = json.loads(text)
            add('feature', 'php')
            for section in ('require', 'require-dev'):
                for name, version in data.get(section, {}).items():
                    add('composer', name, version)
            add('feature', 'php', data.get('require', {}).get('php'), row['path'] + ': require.php')
            value = bounded_text(path.parent / 'composer.lock')
            if value:
                lock = json.loads(value)
                for dep in lock.get('packages', []) + lock.get('packages-dev', []):
                    add('composer', dep['name'], dep.get('version', '').lstrip('v'), row['scope'] + '/composer.lock: resolved dependency')
            for name in ('test', 'lint', 'check'):
                if name in data.get('scripts', {}):
                    row['commands'].append('composer run-script ' + name)
        elif kind in {'nuget', 'dotnet'}:
            add('feature', 'dotnet')
            if kind == 'dotnet':
                data = json.loads(text)
                row['tool_versions']['dotnet-sdk'] = data.get('sdk', {}).get('version')
                row['diagnostics'].append('global.json SDK pin is not a target-framework/runtime version')
            else:
                add('feature', 'csharp')
                root = ET.fromstring(text)
                frameworks = []
                for node in root.iter():
                    name, value = node.tag.rsplit('}', 1)[-1], (node.text or '').strip()
                    if name in {'TargetFramework', 'TargetFrameworks'}:
                        frameworks += value.split(';')
                    elif name == 'LangVersion':
                        add('feature', 'csharp', value, row['path'] + ': LangVersion')
                    elif name == 'PackageReference':
                        version = node.get('Version') or next(((child.text or '') for child in node if child.tag.rsplit('}', 1)[-1] == 'Version'), None)
                        add('nuget', node.get('Include', node.get('Update', '')), version)
                    elif name == 'FrameworkReference':
                        add('nuget', node.get('Include', ''), None)
                row['target_frameworks'] = frameworks
                values = [match.group(1) for framework in frameworks
                          for match in [re.fullmatch(r'net(\d+\.\d+)(?:-[\w.-]+)?', framework)] if match]
                if values:
                    add('feature', 'dotnet', values[0] if len(set(values)) == 1 else ' || '.join('^' + value for value in sorted(set(values))),
                        row['path'] + ': TargetFramework(s), not C# language version', ';'.join(frameworks))
                if root.get('Sdk', '').startswith('Microsoft.NET.Sdk.Web'):
                    add('feature', 'aspnet')
                if frameworks and not values:
                    row['diagnostics'].append('Legacy/portable .NET target is not a modern runtime version; declare SDK/runtime separately')
                row['commands'] = ['dotnet test ' + row['path'] + ' (confirm solution/target frameworks)']
        elif kind == 'pub':
            add('feature', 'dart')
            section, dependency = None, None
            for line in text.splitlines():
                top = re.match(r'^(environment|dependencies|dev_dependencies|dependency_overrides):\s*$', line)
                if top:
                    section = top.group(1)
                elif line and not line[0].isspace() and not line.startswith('#'):
                    section = None
                match = re.match(r"^  ([\w-]+):\s*[\"']([^#\"']*)|^  ([\w-]+):\s*([^#]*)", line)
                if match and section:
                    name, value = (match.group(1), match.group(2)) if match.group(1) else (match.group(3), match.group(4))
                    value = value.strip()
                    if section == 'environment':
                        if name in {'sdk', 'flutter'}:
                            add('feature', 'dart' if name == 'sdk' else 'flutter', value or None, row['path'] + ': environment.' + name)
                    else:
                        dependency = name
                        add('pub', name, value or None)
                if re.match(r'^    sdk:\s*flutter\s*(?:#.*)?$', line) and dependency == 'flutter':
                    add('feature', 'flutter')
            row['diagnostics'].append('Dart and Flutter SDK constraints are distinct; SDK dependency supplies no Flutter version')
        elif kind in {'swift', 'xcode', 'swift-source'}:
            code = re.sub(r'/\*.*?\*/|^\s*//[^\n]*', '', text, flags=re.S | re.M)
            used_ui = bool(re.search(r'^\s*import\s+SwiftUI\b', code, re.M))
            if kind != 'swift-source' or used_ui:
                add('feature', 'swift')
            if kind == 'swift':
                match = re.search(r'^//\s*swift-tools-version:\s*([\d.]+)', text, re.M)
                if match:
                    row['tool_versions']['swift-tools'] = match.group(1)
                row['commands'] = ['swift test (from ' + row['scope'] + '; confirm platforms/toolchain)']
            elif kind == 'xcode':
                match = re.search(r'\bSWIFT_VERSION\s*=\s*([\d.]+)', text)
                if match:
                    row['language_modes']['swift'] = match.group(1)
            if used_ui:
                add('feature', 'swiftui')
            if kind != 'swift-source' or facts:
                row['diagnostics'].append('Swift tools/language mode and SwiftUI SDK availability are not compiler version evidence')
        elif kind == 'cmake':
            code = re.sub(r'#[^\n]*', '', text)
            match = re.search(r'\bproject\s*\([^)]*\bLANGUAGES\s+([^)]*)\)', code, re.I)
            languages = set(re.findall(r'\b(?:C|CXX)\b', match.group(1))) if match else set()
            for key, target, language in [('CMAKE_C_STANDARD', 'c', 'C'), ('CMAKE_CXX_STANDARD', 'cpp', 'CXX')]:
                if re.search(r'\b' + key + r'\b', code):
                    languages.add(language)
                match = re.search(r'\bset\s*\(\s*' + key + r'\s+(\d+)', code, re.I)
                if match:
                    row['language_modes'][target] = match.group(1)
            for language in languages:
                add('feature', 'c' if language == 'C' else 'cpp')
            if not languages:
                row['diagnostics'].append('CMake language not explicit; review project/enable_language/target sources or declare c/cpp')
        elif kind == 'wechat':
            data = json.loads(text)
            if data.get('compileType') == 'miniprogram':
                add('feature', 'wechat')
                row['diagnostics'].append('WeChat base-library/device compatibility needs project settings and real-device review')
        elif kind == 'docker':
            add('feature', 'docker')
            code = re.sub(r'^\s*#[^\n]*', '', text, flags=re.M)
            if path.name == 'Dockerfile':
                images = re.findall(r'^FROM\s+(?:--platform=\S+\s+)?([^\s]+)', code, re.M | re.I)
            else:
                images, in_services, in_service = [], False, False
                for line in code.splitlines():
                    if line and not line[0].isspace():
                        in_services = bool(re.fullmatch(r'services:\s*', line))
                        in_service = False
                    elif in_services and re.fullmatch(r'  [\w.-]+:\s*', line):
                        in_service = True
                    elif in_services and in_service:
                        match = re.match(r"^    image:\s*[\"']?([^\s\"'#]+)", line)
                        if match:
                            images.append(match.group(1))
                if not images:
                    row['diagnostics'].append('Compose image fields missing/unrecognized; complex YAML/anchors require source review')
            for image in images:
                image = re.sub(r'^(?:docker\.io/)?library/', '', image).removeprefix('docker.io/')
                name, _, tag = image.partition(':')
                if '@' in name or '/' in name or '$' in image:
                    continue
                version = re.match(r'^(\d+(?:\.\d+){0,2})(?:-|$)', tag)
                add('image', name, version.group(1) if version else None, row['path'] + ': configured image ' + name + ' (runtime not contacted)')
    except (ET.ParseError, ValueError, TypeError, AttributeError, KeyError) as error:
        if kind == 'npm':
            raise ValueError(str(error)) from None
        facts = []
        row['diagnostics'].append(kind + ' manifest invalid/unparseable: ' + type(error).__name__)
    return stack_definitions.apply(definitions, facts, row)


def major_set(value):
    """Return all constrained majors, or None for unresolved/unbounded selectors."""
    if not isinstance(value, str):
        return None
    value = value.strip()
    if re.fullmatch(r'[~^]?v?\d+(?:\.(?:\d+|[xX*])){0,2}(?:-[\w.-]+)?', value):
        number = re.match(r'[~^]?v?(\d+)', value)
        return {int(number.group(1))}
    if '||' in value:
        parts = [major_set(part) for part in value.split('||')]
        return set().union(*parts) if all(parts) else None
    matches = re.findall(r'(>=|>|<=|<|==|=)\s*v?(\d+(?:\.\d+){0,2})', value)
    if not matches or re.sub(r'(>=|>|<=|<|==|=)\s*v?\d+(?:\.\d+){0,2}|[ ,]', '', value):
        return None
    equals = [int(version.split('.')[0]) for op, version in matches if op in {'==', '='}]
    if equals:
        return {equals[0]} if len(set(equals)) == 1 else None
    lower = [int(version.split('.')[0]) for op, version in matches if op in {'>', '>='}]
    upper = [(op, [int(piece) for piece in version.split('.')])
             for op, version in matches if op in {'<', '<='}]
    if not lower or not upper:
        return None
    # <4 / <4.0 exclude major 4; <4.2 includes it. Never equate a range with a lock.
    end = min(parts[0] - (1 if op == '<' and not any(parts[1:]) else 0) for op, parts in upper)
    start = max(lower)
    return set(range(start, end + 1)) if 0 <= end - start <= 30 else None
