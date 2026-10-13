"""Manifest, version and independent-consumer regression contracts; no application execution."""
import ast
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('coverage_personal', ROOT / 'scripts/personal.py')
personal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(personal)
import stack_definitions
import tools


class StackCoverageTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name).resolve() / 'consumer'
        self.project.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def make(self, name, text):
        path = self.project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def npm(self, deps, **extra):
        return self.make('package.json', json.dumps({'dependencies': deps, **extra}))

    def test_full_grouped_inventory_preserves_official_fallbacks(self):
        expected = set('java kotlin javascript typescript python go rust csharp dotnet php swift dart node c cpp vue react nextjs nuxt angular svelte sveltekit astro spring django fastapi flask express nestjs fastify aspnet laravel gin flutter react-native swiftui electron tauri wechat postgres mysql sqlite mariadb mongodb redis prisma sqlalchemy mybatis hibernate maven gradle vite docker'.split())
        coverage = personal.list_stacks()
        rows = {row['id']: row for group in coverage['groups'] for row in group['stacks']}
        self.assertEqual(set(rows), expected)
        self.assertEqual([group['count'] for group in coverage['groups']], [15, 8, 10, 6, 6, 4, 4])
        for stack in ('react', 'go', 'rust'):
            self.assertEqual(rows[stack]['coverage_state'], 'official_acquisition')
            self.assertTrue(all(profile['kind'] == 'official' for profile in rows[stack]['profiles']))
        self.assertIn('stacks.vue.legacy-v2', {profile['id'] for profile in rows['vue']['profiles']})

    def test_npm_framework_orm_and_ui_detection_uses_exact_dependency_names(self):
        self.npm({'next': '15.3.0', 'nuxt': '3.16.0', '@angular/core': '19.0.0', 'svelte': '5.0.0',
                  '@sveltejs/kit': '2.0.0', 'astro': '5.0.0', 'vite': '6.0.0', 'prisma': '6.0.0',
                  'electron': '34.0.0', '@tauri-apps/api': '2.0.0', 'react-native': '0.78.0'})
        found = personal.detect(self.project)
        self.assertTrue({'nextjs','nuxt','angular','svelte','sveltekit','astro','vite','prisma','electron','tauri','react-native'} <= set(found['stacks']))
        self.assertIn('ui', found['capabilities'])
        self.assertEqual(found['databases'], [])
        self.assertNotIn('node', found['stacks'])

    def test_backend_only_and_false_database_strings_do_not_select_ui_or_engines(self):
        self.npm({'express': '^5.0.0', '@nestjs/core': '^11.0.0', 'fastify': '^5.0.0', 'mysql-helper-docs': '1.0.0'},
                 description='mysql mariadb redis mongodb postgres sqlite', scripts={'test': 'echo mysql'}, engines={'node': '>=22'})
        found = personal.detect(self.project)
        self.assertEqual(found['databases'], [])
        self.assertEqual(found['capabilities'], [])
        self.assertTrue({'express','nestjs','fastify','node'} <= set(found['stacks']))
        self.assertEqual(tools.default_tools(self.project)[0], ['codegraph','rtk','qmd'])

    def test_pnpm_workspace_lock_and_runner_are_scoped(self):
        self.make('package.json', json.dumps({'packageManager': 'pnpm@10.12.1'}))
        self.make('web/package.json', json.dumps({'dependencies': {'vue': '^3.0.0'}, 'scripts': {'test': 'must-not-run', 'build': 'must-not-run'}}))
        self.make('pnpm-lock.yaml', "lockfileVersion: '9.0'\nimporters:\n  .: {}\n  web:\n    dependencies:\n      vue:\n        specifier: ^3.0.0\n        version: 3.5.43(typescript@5.9.0)\n  old:\n    dependencies:\n      vue:\n        specifier: ^2.0.0\n        version: 2.7.16\n")
        row = next(row for row in personal.detect(self.project)['packages'] if row['path'] == 'web/package.json')
        self.assertEqual(row['versions']['vue'], '3.5.43')
        self.assertEqual(row['commands'], ['pnpm run test','pnpm run build'])
        self.assertIn('resolved', row['version_evidence']['vue'])

    def test_yarn_resolves_matching_descriptor_and_bun_uses_actual_script_runner(self):
        self.npm({'vue': '^3.0.0'}, packageManager='yarn@4.0.0', scripts={'test':'never executed'})
        self.make('yarn.lock', '"vue@npm:^3.0.0":\n  version: 3.5.43\n\n"vue@npm:^2.0.0":\n  version: 2.7.16\n')
        row = personal.detect(self.project)['packages'][0]
        self.assertEqual(row['versions']['vue'], '3.5.43')
        self.assertEqual(row['commands'], ['yarn run test'])
        self.npm({'vue':'3.5.43'}, packageManager='bun@1.2.0', scripts={'check':'never executed'})
        row = personal.detect(self.project)['packages'][0]
        self.assertEqual(row['commands'], ['bun run check'])

    def test_kotlin_dsl_does_not_identify_kotlin_application_and_java_alias_retains_raw(self):
        path = self.make('build.gradle.kts', 'plugins { id("java") }\njava { sourceCompatibility = JavaVersion.VERSION_1_8 }\n')
        row = personal.detect(self.project)['packages'][0]
        self.assertEqual(row['stacks'], ['gradle','java'])
        self.assertEqual(row['versions']['java'], '8')
        self.assertEqual(row['raw_versions']['java'], 'VERSION_1_8')
        path.write_text('plugins { kotlin("jvm") version "2.1.0"; id("org.springframework.boot") version "3.4.0" }\n')
        row = personal.detect(self.project)['packages'][0]
        self.assertIn('kotlin', row['stacks'])
        self.assertEqual(row['versions']['kotlin'], '2.1.0')
        self.assertEqual(row['versions']['spring'], '3.4.0')

    def test_boot_two_java_eight_and_vue_two_get_only_their_legacy_profiles(self):
        self.make('api/pom.xml', '<project xmlns="http://maven.apache.org/POM/4.0.0"><parent><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-parent</artifactId><version>2.7.18</version></parent><properties><java.version>1.8</java.version></properties></project>')
        self.make('web/package.json', json.dumps({'dependencies': {'vue':'2.7.16'}}))
        result = personal.install(self.project, offline=True)
        self.assertEqual(result['spec_sources_state'], 'acquired')
        self.assertTrue({'stacks.vue.legacy-v2','stacks.spring.legacy-v2','stacks.java'} <= set(result['rules']))
        self.assertNotIn('stacks.vue', result['rules'])
        self.assertNotIn('stacks.spring', result['rules'])
        row = result['detected']['packages'][0]
        self.assertEqual(row['versions']['java'], '8')
        self.assertEqual(row['raw_versions']['java'], '1.8')

    def test_unknown_and_future_vue_major_do_not_guess_a_version_profile(self):
        self.npm({'vue':'workspace:*'})
        result = personal.install(self.project, offline=True)
        self.assertFalse({'stacks.vue','stacks.vue.legacy-v2'} & set(result['rules']))
        self.assertEqual(result['spec_sources_state'], 'incomplete')
        self.npm({'vue':'4.0.0'})
        report, _, _ = personal.query_stacks(self.project, offline=True)
        row = next(row for row in report['packages'] if row['stack']=='vue')
        self.assertEqual(row['status'], 'version_mismatch')

    def test_python_multiline_dependencies_and_pep_name_normalization(self):
        self.make('pyproject.toml', '[project]\nrequires-python=">=3.10,<4"\ndependencies=[\n "FastAPI>=0.110",\n "SQLAlchemy>=2.0",\n "psycopg2_binary==2.9.0",\n]\n[project.optional-dependencies]\nadmin=["Django==5.2", "Flask==3.1"]\n')
        found = personal.detect(self.project)
        self.assertTrue({'python','fastapi','sqlalchemy','django','flask'} <= set(found['stacks']))
        self.assertEqual(found['databases'], ['postgres'])
        self.assertNotIn('postgres', found['packages'][0]['versions'])
        self.assertEqual(found['capabilities'], ['database'])

    def test_python39_partial_toml_is_diagnosed_and_common_version_gap_is_visible(self):
        self.make('pyproject.toml', '[project]\nrequires-python=">=3.10,<4"\ndependencies=["fastapi>=0.110"]\n')
        with patch.object(personal.stack_facts, 'tomllib', None):
            found = personal.detect(self.project)
        self.assertIn('fastapi', found['stacks'])
        self.assertTrue(any('Full TOML unavailable' in text for text in found['diagnostics']))
        self.npm({'express':'workspace:*'})
        report, assets, _ = personal.query_stacks(self.project, offline=True)
        row = next(row for row in report['packages'] if row['stack']=='express')
        self.assertEqual(row['status'], 'acquired')
        self.assertEqual(row['version_state'], 'unbounded_or_unparseable')
        self.assertIn(b'Release compatibility remains pending', assets[row['target']])

    def test_dotnet_sdk_target_framework_and_csharp_version_are_distinct(self):
        self.make('api.csproj', '<Project Sdk="Microsoft.NET.Sdk.Web"><PropertyGroup><TargetFrameworks>net8.0;net9.0</TargetFrameworks><LangVersion>12.0</LangVersion></PropertyGroup><ItemGroup><PackageReference Include="Npgsql" Version="8.0.0"/></ItemGroup></Project>')
        self.make('global.json', '{"sdk":{"version":"9.0.300"}}')
        found = personal.detect(self.project)
        row = next(row for row in found['packages'] if row['path']=='api.csproj')
        self.assertTrue({'csharp','dotnet','aspnet'} <= set(row['stacks']))
        self.assertEqual(row['versions']['csharp'], '12.0')
        self.assertEqual(row['versions']['dotnet'], '^8.0 || ^9.0')
        self.assertNotIn('postgres', row['versions'])
        sdk = next(row for row in found['packages'] if row['path']=='global.json')
        self.assertEqual(sdk['tool_versions']['dotnet-sdk'], '9.0.300')
        self.assertNotIn('dotnet', sdk['versions'])

    def test_dart_and_flutter_sdk_constraints_are_independent(self):
        path = self.make('pubspec.yaml', 'name: fixture\nenvironment:\n  sdk: ">=3.4.0 <4.0.0"\ndependencies:\n  flutter:\n    sdk: flutter\n')
        row = personal.detect(self.project)['packages'][0]
        self.assertEqual(row['versions']['dart'], '>=3.4.0 <4.0.0')
        self.assertIn('flutter', row['stacks'])
        self.assertNotIn('flutter', row['versions'])
        path.write_text('name: fixture\nenvironment:\n  sdk: ">=3.4.0 <4.0.0"\n  flutter: ">=3.24.0"\ndependencies:\n  flutter:\n    sdk: flutter\n')
        self.assertEqual(personal.detect(self.project)['packages'][0]['versions']['flutter'], '>=3.24.0')

    def test_swiftui_usage_and_xcode_language_mode_do_not_invent_compiler_version(self):
        self.make('Package.swift', '// swift-tools-version: 6.0\nimport PackageDescription\n')
        self.make('Sources/View.swift', 'import SwiftUI\nstruct ViewModel {}\n')
        self.make('App.xcodeproj/project.pbxproj', 'SWIFT_VERSION = 5.0;\nSDKROOT = iphoneos;\n')
        found = personal.detect(self.project)
        self.assertTrue({'swift','swiftui'} <= set(found['stacks']))
        self.assertTrue(all('swift' not in row['versions'] and 'swiftui' not in row['versions'] for row in found['packages']))
        xcode = next(row for row in found['packages'] if row['path'].endswith('project.pbxproj'))
        self.assertEqual(xcode['language_modes']['swift'], '5.0')
        self.assertIn('ui', found['capabilities'])

    def test_cmake_standards_and_wechat_project_markers_are_precise(self):
        self.make('native/CMakeLists.txt', 'project(example LANGUAGES C CXX)\nset(CMAKE_CXX_STANDARD 20)\nset(CMAKE_C_STANDARD 11)\n')
        self.make('app.json', '{"pages":["pages/home/index"]}')
        found = personal.detect(self.project)
        self.assertEqual(found['stacks'], ['c','cpp'])
        self.assertEqual(found['packages'][0]['language_modes'], {'c':'11','cpp':'20'})
        self.assertEqual(found['packages'][0]['versions'], {})
        self.make('project.config.json','{"compileType":"miniprogram","miniprogramRoot":"app/"}')
        self.assertIn('wechat', personal.detect(self.project)['stacks'])

    def test_composer_go_and_cargo_frameworks_use_real_dependency_fields(self):
        self.make('php/composer.json', '{"require":{"php":"^8.3","laravel/framework":"^12.0","mongodb/mongodb":"^2.0"},"scripts":{"test":"never-run"}}')
        self.make('php/composer.lock', '{"packages":[{"name":"laravel/framework","version":"v12.3.0"}]}')
        self.make('go/go.mod', 'module fixture\ngo 1.24.0\nrequire (\n github.com/gin-gonic/gin v1.10.0\n github.com/redis/go-redis/v9 v9.0.0\n)\n')
        self.make('rust/Cargo.toml', '[package]\nrust-version="1.85"\n[dependencies]\ntauri={version="2.3.0"}\n')
        found = personal.detect(self.project)
        self.assertTrue({'php','laravel','go','gin','rust','tauri'} <= set(found['stacks']))
        self.assertEqual(found['databases'], ['mongodb','redis'])
        php = next(row for row in found['packages'] if row['path']=='php/composer.json')
        self.assertEqual(php['versions']['laravel'], '12.3.0')
        self.assertEqual(php['commands'], ['composer run-script test'])

    def test_database_driver_server_and_provider_routes_remain_separate(self):
        self.npm({'mysql2':'3.12.0','mariadb':'3.3.0','mongodb':'6.0.0','ioredis':'5.0.0'})
        found = personal.detect(self.project)
        self.assertEqual(found['databases'], ['mariadb','mongodb','mysql','redis'])
        self.assertTrue(all(engine not in found['packages'][0]['versions'] for engine in found['databases']))
        names, route = tools.default_tools(self.project)
        self.assertIn('dbhub', names)
        self.assertEqual(route['pending_engines'], ['mongodb','redis'])
        self.npm({'mongodb':'6.0.0','redis':'4.0.0'})
        names, route = tools.default_tools(self.project)
        self.assertNotIn('dbhub', names)
        self.assertEqual(route['state'], 'provider_selection_pending')
        result = personal.install(self.project, offline=True)
        self.assertIn('tools.database.usage', result['rules'])
        self.assertNotIn('ui', result['selected_capabilities'])

    def test_container_images_only_supply_configured_targets_not_driver_versions(self):
        self.make('Dockerfile', 'FROM node:22.14-alpine AS build\nRUN echo mysql:8.0\n')
        self.make('compose.yaml', 'services:\n  data:\n    image: postgres:17.4\n  custom:\n    image: company/mysql:9.0\n')
        found = personal.detect(self.project)
        self.assertEqual(found['databases'], ['postgres'])
        self.assertIn('docker', found['stacks'])
        row = next(row for row in found['packages'] if row['path']=='compose.yaml')
        self.assertEqual(row['versions']['postgres'], '17.4')
        self.assertIn('runtime not contacted', row['version_evidence']['postgres'])

    def test_conflicting_runtime_manifests_stay_incomplete_and_preserve_both_facts(self):
        self.npm({}, engines={'node':'^24.0.0'})
        self.make('Dockerfile','FROM node:22.14-alpine\n')
        report, _, _ = personal.query_stacks(self.project, offline=True)
        row = next(row for row in report['packages'] if row['stack']=='node')
        self.assertEqual(row['status'],'version_conflict')
        self.assertEqual({fact['version'] for fact in row['version_facts']},{'^24.0.0','22.14'})
        self.assertFalse(report['acquisition_complete'])
        self.assertIn('同包清单版本冲突', personal.stack_sources.chinese_report(report).decode())

    def test_non_sql_default_tool_cli_records_pending_without_installing_dbhub(self):
        self.npm({'mongodb':'6.0.0'})
        base = {'tools':{}, 'pending':[], 'overall_complete':True}
        with patch.object(tools,'initialize',return_value=base) as initialize, patch.object(sys,'argv',['tools.py','--project',str(self.project)]):
            self.assertEqual(tools.main(),2)
        self.assertNotIn('dbhub',initialize.call_args.args[1])
        report = json.loads((self.project/'.trellis/personal/tool-report.json').read_text())
        self.assertFalse(report['overall_complete'])
        self.assertIn('database:compatible_provider_selection_pending',report['pending'])

    def test_commented_swiftui_and_compose_environment_example_do_not_identify_targets(self):
        self.make('Sample.swift','/*\nimport SwiftUI\n*/\nimport Foundation\n')
        self.make('compose.yaml','services:\n  worker:\n    environment:\n      EXAMPLE: |\n        image: mysql:8.0\n')
        found = personal.detect(self.project)
        self.assertNotIn('swiftui',found['stacks'])
        self.assertEqual(found['databases'],[])

    def test_symlinks_ignored_dirs_oversize_and_invalid_manifests_remain_observable(self):
        outside = Path(self.temp.name) / 'outside'
        outside.mkdir()
        (outside/'package.json').write_text('{"dependencies":{"mysql2":"3"}}')
        (self.project/'linked').symlink_to(outside, target_is_directory=True)
        self.make('node_modules/nested/package.json', '{"dependencies":{"redis":"4"}}')
        self.make('huge/package.json', 'x' * 1_000_001)
        self.make('bad/pom.xml', '<not-valid')
        found = personal.detect(self.project)
        self.assertEqual(found['stacks'], [])
        self.assertEqual(found['databases'], [])
        self.assertTrue(any('oversized' in item for item in found['diagnostics']))
        self.assertTrue(any('unparseable' in item for item in found['diagnostics']))

    def test_unsupported_schema_marker_and_stale_generation_are_rejected(self):
        library = Path(self.temp.name).resolve() / 'library'
        shutil.copytree(ROOT, library, ignore=shutil.ignore_patterns('node_modules','dist','__pycache__','.git'))
        path = library/'stack-definitions.json'
        data = json.loads(path.read_text())
        data['stacks'][0]['markers'][0]['version'] = 'false'
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'Invalid marker'):
            stack_definitions.load(library)
        data['stacks'][0]['markers'][0]['version'] = True
        data['stacks'][0]['summary_zh'] += ' changed'
        path.write_text(json.dumps(data))
        with patch.object(personal, 'LIBRARY', library):
            with self.assertRaisesRegex(ValueError, 'Stale generated coverage'):
                personal.validate()
            personal.build()
            self.assertEqual(personal.validate()['stack_ids'], 53)
            process = library/'specs/process/bootstrap.md'
            process.write_text(process.read_text()+'\nSource contract changed.\n')
            with self.assertRaisesRegex(ValueError, 'Stale generated bundle source'):
                personal.validate()

    def test_independent_installed_copy_runs_detection_query_inventory_and_validation(self):
        self.make('service/requirements.txt', 'fastapi==0.115.0\nsqlalchemy==2.0.0\npymysql==1.1.0\n')
        self.make('service/.python-version','3.12.0\n')
        self.make('.trellis/config.yaml', 'codex:\n  dispatch_mode: inline\n')
        self.make('AGENTS.md','Consumer policy: preserve this.\n')
        result = personal.install(self.project, offline=True)
        self.assertEqual(result['spec_sources_state'], 'acquired')
        helper = self.project/'.trellis/personal/personal.py'
        for command in ('detect','query-stacks','list-stacks','validate'):
            argv = [sys.executable,str(helper),command,'--project',str(self.project)]
            if command == 'query-stacks':
                argv.append('--offline')
            process = subprocess.run(argv,cwd=self.project,capture_output=True,text=True,timeout=30)
            self.assertEqual(process.returncode,0,process.stderr+process.stdout)
            parsed = json.loads(process.stdout)
            self.assertNotIn(str(ROOT), process.stdout)
            if command == 'list-stacks':
                self.assertEqual(parsed['total_stacks'],53)
        self.assertEqual((self.project/'.trellis/config.yaml').read_text(),'codex:\n  dispatch_mode: inline\n')
        self.assertTrue((self.project/'AGENTS.md').read_text().startswith('Consumer policy: preserve this.'))
        self.assertFalse((self.project/'.trellis/spec/guides/personal/stacks/flutter').exists())
        self.assertNotIn('tools.ui-design',result['rules'])
        library = self.project/'.trellis/personal/library'
        for path in ('stack-definitions.json','STACKS.zh-CN.md','scripts/stack_definitions.py'):
            self.assertEqual((library/path).read_bytes(),(ROOT/path).read_bytes())
        markdown = subprocess.run([sys.executable,str(helper),'list-stacks','--format','markdown'],cwd=self.project,capture_output=True,text=True,timeout=30)
        self.assertEqual(markdown.returncode,0,markdown.stderr)
        self.assertIn('53 个技术栈入口',markdown.stdout)
        for file in (self.project/'.trellis/spec/guides/personal').rglob('index.md'):
            for link in re.findall(r'\[[^]]*\]\(([^)]+)\)',file.read_text()):
                if not link.startswith('https:'):
                    self.assertTrue((file.parent/link).exists(), str(file)+': '+link)

    def test_all_helpers_keep_python39_syntax(self):
        for path in (ROOT/'scripts').glob('*.py'):
            ast.parse(path.read_text(),filename=str(path),feature_version=(3,9))

    def test_gradle_only_parses_dependency_calls_and_ignores_comment_coordinates(self):
        self.make('build.gradle.kts', '''plugins { id("java") }
val example = "org.postgresql:postgresql:42.7.0"
val docs = """implementation("org.postgresql:postgresql:42.7.0")
id("org.springframework.boot") version "2.7.18"
"""
dependencies {
    implementation("org.hibernate.orm:hibernate-core:6.6.0") // "redis.clients:jedis:5.0.0"
    runtimeOnly("com.mysql:mysql-connector-j:9.0.0")
    // implementation("org.mongodb:mongodb-driver-sync:5.0.0")
}
''')
        found = personal.detect(self.project)
        self.assertEqual(found['databases'], ['mysql'])
        self.assertIn('hibernate', found['stacks'])
        self.assertNotIn('spring', found['stacks'])

    def test_nearest_runner_lock_owns_nested_package_when_no_manager_declared(self):
        self.make('yarn.lock', '"vue@^2.0.0":\n  version "2.7.16"\n')
        self.make('web/package.json', json.dumps({'dependencies': {'vue': '^3.0.0'}, 'scripts': {'test': 'never-run'}}))
        self.make('web/package-lock.json', json.dumps({'packages': {'node_modules/vue': {'version': '3.5.43'}}}))
        row = personal.detect(self.project)['packages'][0]
        self.assertEqual(row['package_manager'], 'npm')
        self.assertEqual(row['versions']['vue'], '3.5.43')
        self.assertEqual(row['commands'], ['npm run test'])

    def test_same_manifest_runtime_constraint_conflicts_remain_incomplete(self):
        self.npm({}, engines={'node': '^24.0.0'})
        self.make('.nvmrc', '22.14.0\n')
        report, _, _ = personal.query_stacks(self.project, offline=True)
        row = next(row for row in report['packages'] if row['stack'] == 'node')
        self.assertEqual(row['status'], 'version_conflict')
        self.assertEqual({fact['version'] for fact in row['version_facts']}, {'^24.0.0', '22.14.0'})
        self.assertFalse(report['acquisition_complete'])

    def test_explicit_personal_profile_excludes_conflicting_bundled_rule(self):
        self.npm({'vue': '3.5.43'})
        raw = b'# Team Vue policy\nUse the established team components.\n'
        self.make('registry/vue.md', raw.decode())
        registry = self.make('registry/stack-sources.json', json.dumps({'schema_version': 1, 'profiles': [{
            'id': 'team.vue', 'stack': 'vue', 'kind': 'personal', 'major_versions': [3],
            'license': 'fixture', 'coverage': ['team components'],
            'source': {'path': 'vue.md', 'sha256': personal.digest(raw)}
        }]}))
        result = personal.install(self.project, stack_registry=str(registry), offline=True)
        self.assertEqual(result['spec_sources_state'], 'acquired')
        self.assertNotIn('stacks.vue', result['rules'])
        self.assertFalse((self.project / '.trellis/spec/guides/personal/stacks/vue/index.md').exists())

    def test_caret_zero_and_tilde_major_declarations_obey_semver_bounds(self):
        matches = personal.stack_sources.declaration_matches
        self.assertFalse(matches('^0.115.0', '0.116.0'))
        self.assertTrue(matches('^0.115.0', '0.115.2'))
        self.assertFalse(matches('^0.0.3', '0.0.4'))
        self.assertTrue(matches('~22', '22.14.0'))

    def test_definition_reader_rejects_linked_oversized_and_malformed_metadata(self):
        path = self.project / 'stack-definitions.json'
        path.symlink_to(ROOT / 'stack-definitions.json')
        with self.assertRaisesRegex(ValueError, 'linked'):
            stack_definitions.load(self.project)
        path.unlink()
        path.write_text(' ' * 1_000_001)
        with self.assertRaisesRegex(ValueError, 'oversized'):
            stack_definitions.load(self.project)
        data = json.loads((ROOT / 'stack-definitions.json').read_text())
        data['groups'][0]['title_zh'] = ['invalid title']
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'Invalid stack group'):
            stack_definitions.load(self.project)


if __name__ == '__main__':
    unittest.main()
