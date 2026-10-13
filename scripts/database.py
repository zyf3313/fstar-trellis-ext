#!/usr/bin/env python3
"""Configure one DBHub provider from explicit local source/credential references."""
import argparse
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

from personal import LIBRARY, json_bytes, load, safe, stamp, write
from tools import merge_codex, npm_tool, toml_value
from mcp_stdio import MCPClient


def configuration(project, manifest, environ=None):
    environ = os.environ if environ is None else environ
    sources = manifest.get('sources', [])
    if not sources:
        return None, {'status': 'not_applicable', 'sources': []}
    ids, tool_names = set(), set()
    lines, records, missing = [], [], []
    for source in sources:
        source_id = source['id']
        reference = source['dsn_env']
        if not re.fullmatch(r'[a-z][a-z0-9_]{0,63}', source_id) or source_id in ids:
            raise ValueError('Invalid or duplicate database source ID')
        if not re.fullmatch(r'[A-Z][A-Z0-9_]*', reference):
            raise ValueError('Credential must be a local environment-variable reference')
        if source.get('engine') not in {'postgres', 'mysql', 'sqlite'}:
            raise ValueError('Engine adapter is not yet verified')
        if source.get('environment') not in {'development', 'test', 'staging', 'production'}:
            raise ValueError('Explicit database environment is required')
        if not isinstance(source.get('readonly'), bool):
            raise ValueError('Explicit readonly capability is required')
        if source['environment'] == 'production' and not source['readonly']:
            raise ValueError('Production write setup requires a separately reviewed project adapter')
        ids.add(source_id)
        value = environ.get(reference)
        if not value:
            missing.append(reference)
        else:
            scheme = urlsplit(value).scheme
            if scheme not in {'postgres': {'postgres', 'postgresql'}, 'mysql': {'mysql'},
                              'sqlite': {'sqlite'}}[source['engine']]:
                raise ValueError('Credential scheme does not match declared engine: ' + source_id)
        records.append({key: source[key] for key in ['id', 'dsn_env', 'engine', 'environment', 'readonly']})
        lines.extend(['[[sources]]', 'id = ' + toml_value(source_id),
                      'dsn = ' + toml_value('${' + reference + '}'),
                      'connection_timeout = 10', 'query_timeout = 5', '',
                      '[[tools]]', 'name = "search_objects"', 'source = ' + toml_value(source_id), '',
                      '[[tools]]', 'name = "execute_sql"', 'source = ' + toml_value(source_id),
                      'readonly = ' + toml_value(source['readonly']), 'max_rows = 20', ''])
        for tool in source.get('custom_tools', []):
            name = tool['name']
            if not re.fullmatch(r'[a-z][a-z0-9_]{0,63}', name) or name in tool_names or name in {'execute_sql', 'search_objects'}:
                raise ValueError('Invalid or duplicate custom tool name')
            tool_names.add(name)
            statement = safe(project, tool['statement_file']).read_text()
            if not statement.strip() or len(statement) > 100_000 or not tool.get('description'):
                raise ValueError('Reviewed bounded statement and description are required')
            lines.extend(['[[tools]]', 'name = ' + toml_value(name), 'source = ' + toml_value(source_id),
                          'description = ' + toml_value(tool['description']), 'statement = ' + toml_value(statement),
                          'readonly = ' + toml_value(source['readonly']), 'max_rows = 20'])
            parameter_names = set()
            for parameter in tool.get('parameters', []):
                if not re.fullmatch(r'[a-z][a-z0-9_]*', parameter['name']) or parameter['name'] in parameter_names:
                    raise ValueError('Invalid or duplicate parameter name')
                if parameter['type'] not in {'string', 'integer', 'float', 'boolean', 'array'} or not parameter.get('description'):
                    raise ValueError('Invalid parameter type or missing description')
                parameter_names.add(parameter['name'])
                lines.append('[[tools.parameters]]')
                for key in ['name', 'type', 'description']:
                    lines.append(key + ' = ' + toml_value(parameter[key]))
            lines.append('')
    return ('\n'.join(lines) + '\n').encode(), {
        'status': 'missing_credentials' if missing else 'ready_for_connection',
        'missing_references': missing, 'sources': records}


def payload(result):
    for item in result.get('content', []):
        if item.get('type') == 'text':
            try:
                return json.loads(item['text'])
            except ValueError:
                continue
    if result.get('structuredContent'):
        return result['structuredContent']
    raise RuntimeError('Database tool returned no inspectable JSON result')


def discover_name(tools, base, source_id, single):
    candidates = [tool['name'] for tool in tools if tool['name'] in
                  ({base} if single else {base + '_' + source_id, source_id + '_' + base})]
    if len(candidates) != 1:
        raise RuntimeError('Unexpected DBHub tool naming; inspect actual tools/list before calling')
    return candidates[0]


def initialize(project, manifest, connect=False):
    content, report = configuration(project, manifest)
    if content is None or report['status'] == 'missing_credentials':
        write(safe(project, '.trellis/personal/database-report.json'), json_bytes(report))
        return report
    binary, installation = npm_tool(project, load(LIBRARY / 'tools.lock.json')['tools']['dbhub'])
    config = safe(project, '.trellis/personal/private/dbhub.toml')
    if config.exists() and config.read_bytes() != content:
        candidate = config.with_suffix('.candidate.toml')
        write(candidate, content)
        return {**report, 'status': 'config_conflict', 'candidate': str(candidate.relative_to(project))}
    write(config, content)
    command = [str(binary), '--transport', 'stdio', '--config', str(config)]
    report.update({'installation': installation, 'version': '1.5.0',
                   'status': 'configured_connection_pending', 'write_validation': 'not_performed_by_init'})
    if connect:
        with MCPClient(command, project, safe(project, '.trellis/personal/evidence/' + stamp() + '-database.log')) as client:
            initialized = client.initialize(project)
            tools = client.tools()
            report['server'] = initialized['serverInfo']
            report['tool_names'] = [tool['name'] for tool in tools]
            for source in report['sources']:
                name = discover_name(tools, 'execute_sql', source['id'], len(report['sources']) == 1)
                result = payload(client.call(name, {'sql': 'SELECT 1 AS personal_connection_probe'}))
                if not result.get('success'):
                    raise RuntimeError('Read probe failed: ' + source['id'])
                source['connection_read'] = 'passed'
            report['status'] = 'connection_read_passed'
    config_row = {
        'command': str(binary), 'args': command[1:], 'cwd': str(project),
        'env_vars': [row['dsn_env'] for row in report['sources']],
        'startup_timeout_sec': 30}
    if 'tool_names' in report:
        config_row['enabled_tools'] = report['tool_names']
    report['codex'] = merge_codex(project, {'personal_database': config_row})
    write(safe(project, '.trellis/personal/database-report.json'), json_bytes(report))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--manifest', required=True, help='Project-relative JSON, containing no credential values')
    parser.add_argument('--connect', action='store_true', help='Actually connect and run bounded read probes')
    args = parser.parse_args()
    project = args.project.resolve()
    try:
        report = initialize(project, load(safe(project, args.manifest)), args.connect)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2 if report['status'] in {'config_conflict', 'missing_credentials'} else 0
    except (OSError, ValueError, RuntimeError) as error:
        print(json.dumps({'status': 'failed', 'error_type': type(error).__name__,
                          'detail': 'Inspect private local evidence; credentials are not printed'}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
