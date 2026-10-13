#!/usr/bin/env python3
"""Real DBHub PostgreSQL/MySQL acceptance in uniquely owned disposable containers."""
import argparse
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from database import configuration, discover_name, payload
from mcp_stdio import MCPClient, MCPError
from personal import json_bytes, stamp, write
from tools import toml_value


def docker(args, input_text=None, timeout=60, required=True):
    result = subprocess.run(['docker'] + args, input=input_text, text=True, capture_output=True, timeout=timeout)
    if required and result.returncode:
        raise RuntimeError('Docker fixture command failed: ' + ' '.join(args[:2]))
    return result


def call(client, name, arguments):
    result = payload(client.call(name, arguments))
    if not result.get('success'):
        raise RuntimeError('Unexpected database tool failure: ' + name)
    return result['data']


def rows(data):
    return data['statements'][-1]['rows']


def rejected(client, name, arguments):
    try:
        client.call(name, arguments)
    except MCPError:
        return True
    raise AssertionError('Expected a real denied/error result: ' + name)


def verify_engine(binary, evidence, engine, image):
    name = 'personal-trellis-' + engine + '-' + secrets.token_hex(4)
    password = secrets.token_hex(16)
    root_password = secrets.token_hex(16)
    environment = evidence / (name + '.env')
    values = {'POSTGRES_PASSWORD': password, 'POSTGRES_USER': 'app', 'POSTGRES_DB': 'personal'} if engine == 'postgres' else {
        'MYSQL_ROOT_PASSWORD': root_password, 'MYSQL_USER': 'app', 'MYSQL_PASSWORD': password, 'MYSQL_DATABASE': 'personal'}
    write(environment, ''.join(key + '=' + value + '\n' for key, value in values.items()).encode())
    port = 5432 if engine == 'postgres' else 3306
    container = None
    report = {'engine': engine, 'image': image, 'checks': [], 'write_scope': 'disposable fixture only'}
    try:
        container = docker(['run', '-d', '--rm', '--name', name, '--label', 'personal-trellis.fixture=true',
                            '--env-file', str(environment), '-p', '127.0.0.1::' + str(port), image], timeout=90).stdout.strip()
        report['image_id'] = docker(['inspect', '--format', '{{.Image}}', name]).stdout.strip()
        def sql(statement, required=True):
            if engine == 'postgres':
                args = ['exec', '-i', name, 'psql', '-U', 'app', '-d', 'personal', '-v', 'ON_ERROR_STOP=1', '-At']
            else:
                args = ['exec', '-i', '-e', 'MYSQL_PWD=' + root_password, name, 'mysql', '-uroot', '--batch', '--skip-column-names', 'personal']
            return docker(args, statement, timeout=10, required=required)
        deadline = time.monotonic() + 150
        while time.monotonic() < deadline:
            if sql('SELECT 1;', required=False).returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError('Database initialization exceeded bounded deadline')
        report['database_version'] = sql('SELECT version();').stdout.strip()
        sql("CREATE TABLE personal_probe (id VARCHAR(64) PRIMARY KEY, title VARCHAR(128) NOT NULL);"
            "INSERT INTO personal_probe VALUES ('seed1','种子一'),('seed2','种子二');")
        if engine == 'postgres':
            sql("CREATE ROLE reader LOGIN PASSWORD '" + password + "'; GRANT USAGE ON SCHEMA public TO reader;"
                "GRANT SELECT ON personal_probe TO reader;")
        else:
            sql("CREATE USER 'reader'@'%' IDENTIFIED BY '" + password + "';"
                "GRANT SELECT ON personal.* TO 'reader'@'%';")
        host_port = docker(['port', name, str(port) + '/tcp']).stdout.strip().rsplit(':', 1)[1]
        env = dict(os.environ)
        for key, user in [('PERSONAL_RW_DSN', 'app'), ('PERSONAL_RO_DSN', 'reader')]:
            env[key] = engine + '://' + user + ':' + password + '@127.0.0.1:' + host_port + '/personal?sslmode=disable'
        sources = [{'id': key, 'engine': engine, 'dsn_env': ref, 'environment': 'test', 'readonly': readonly}
                   for key, ref, readonly in [('fixture_rw', 'PERSONAL_RW_DSN', False), ('fixture_ro', 'PERSONAL_RO_DSN', True)]]
        content, configured = configuration(evidence, {'sources': sources}, env)
        assert configured['status'] == 'ready_for_connection'
        content = content.replace(b'query_timeout = 5', b'query_timeout = 1')
        placeholders = ('$1', '$2') if engine == 'postgres' else ('?', '?')
        for source in ['fixture_rw', 'fixture_ro']:
            content += ('\n[[tools]]\nname = "insert_' + source + '"\nsource = "' + source + '"\n'
                        'description = "Insert one explicitly scoped disposable fixture row"\nstatement = ' +
                        toml_value('INSERT INTO personal_probe (id,title) VALUES (' + ','.join(placeholders) + ')') + '\n'
                        '[[tools.parameters]]\nname = "id"\ntype = "string"\ndescription = "Unique fixture id"\n'
                        '[[tools.parameters]]\nname = "title"\ntype = "string"\ndescription = "Bound title"\n').encode()
        config = evidence / (name + '.toml')
        write(config, content)
        command = [str(binary), '--transport', 'stdio', '--config', str(config)]
        with MCPClient(command, evidence, evidence / (name + '-mcp.log'), env=env, timeout=20) as client:
            report['server'] = client.initialize(evidence)['serverInfo']
            tools = client.tools()
            report['tools'] = [tool['name'] for tool in tools]
            execute = discover_name(tools, 'execute_sql', 'fixture_rw', False)
            ro_execute = discover_name(tools, 'execute_sql', 'fixture_ro', False)
            search = discover_name(tools, 'search_objects', 'fixture_rw', False)
            schema = call(client, search, {'object_type': 'table', 'pattern': 'personal_probe', 'detail_level': 'full', 'limit': 3})
            assert 'personal_probe' in json.dumps(schema)
            report['checks'].append('actual_schema')
            samples = rows(call(client, ro_execute, {'sql': 'SELECT id,title FROM personal_probe ORDER BY id LIMIT 2'}))
            assert len(samples) == 2, 'Expected exactly two seeded rows'
            report['checks'].append('bounded_read')
            malicious_literal = "中文 O'Reilly'); DROP TABLE personal_probe; --"
            inserted = call(client, 'insert_fixture_rw', {'id': 'bound1', 'title': malicious_literal})
            assert inserted['statements'][0]['count'] == 1, 'Expected one affected row'
            actual = rows(call(client, ro_execute, {'sql': "SELECT title FROM personal_probe WHERE id='bound1'"}))
            assert actual[0]['title'] == malicious_literal, 'Parameter literal did not round trip exactly'
            report['checks'].append('parameterized_write_affected_rows_and_readback')
            rejected(client, 'insert_fixture_ro', {'id': 'denied1', 'title': 'must fail by database account'})
            report['checks'].append('database_account_write_denied')
            rejected(client, ro_execute, {'sql': "DELETE FROM personal_probe WHERE id='seed1'"})
            report['checks'].append('readonly_tool_write_denied')
            begin = 'BEGIN' if engine == 'postgres' else 'START TRANSACTION'
            call(client, execute, {'sql': begin + "; INSERT INTO personal_probe VALUES ('rolled','rollback'); ROLLBACK;"})
            assert not rows(call(client, ro_execute, {'sql': "SELECT id FROM personal_probe WHERE id='rolled'"})), 'Explicit rollback visible to independent reader'
            report['checks'].append('single_call_explicit_rollback')
            call(client, execute, {'sql': begin + "; INSERT INTO personal_probe VALUES ('committed','commit'); COMMIT;"})
            assert rows(call(client, ro_execute, {'sql': "SELECT id FROM personal_probe WHERE id='committed'"})), 'Commit not visible to independent reader'
            report['checks'].append('single_call_commit_readback')
            rejected(client, execute, {'sql': begin + "; INSERT INTO personal_probe VALUES ('failedbatch','error');"
                                              " INSERT INTO personal_probe VALUES ('seed1','duplicate'); COMMIT;"})
            assert not rows(call(client, ro_execute, {'sql': "SELECT id FROM personal_probe WHERE id='failedbatch'"})), 'Failed batch committed partially'
            report['checks'].append('failed_batch_independent_readback_no_commit')
            # An error leaves engine-specific session state. Never infer its rollback from the transport result.
            call(client, execute, {'sql': 'ROLLBACK;'})
            sleep = 'SELECT pg_sleep(8)' if engine == 'postgres' else 'SELECT SLEEP(8)'
            try:
                outcome = call(client, execute, {'sql': begin + "; INSERT INTO personal_probe VALUES ('timeoutrow','timeout'); " + sleep + '; COMMIT;'})
                report['timeout_transport'] = 'returned_success_check_actual_outcome'
                report['timeout_statement_counts'] = [statement['count'] for statement in outcome['statements']]
            except MCPError:
                report['timeout_transport'] = 'tool_error_outcome_unknown_until_readback'
            unknown = rows(call(client, ro_execute, {'sql': "SELECT id FROM personal_probe WHERE id='timeoutrow'"}))
            report['timeout_reconciliation'] = 'committed' if unknown else 'no_commit_visible'
            report['checks'].append('timeout_outcome_reconciled_without_retry')
            call(client, execute, {'sql': 'ROLLBACK;'})
        report['status'] = 'passed'
        return report
    finally:
        write(evidence / (engine + '-partial.json'), json_bytes(report))
        if container:
            docker(['rm', '-f', name], required=False, timeout=30)
        environment.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    report = {'provider': 'DBHub', 'package_version': '1.5.0', 'engines': [], 'status': 'running'}
    path = evidence / 'database-acceptance.json'
    try:
        for engine, image in [('postgres', 'postgres:17-alpine'), ('mysql', 'mysql:8.4')]:
            result = verify_engine(args.binary.resolve(), evidence, engine, image)
            report['engines'].append(result)
            write(path, json_bytes(report))
            print(json.dumps({'engine': engine, 'status': result['status'], 'checks': len(result['checks'])}), flush=True)
        report['status'] = 'passed'
        write(path, json_bytes(report))
        return 0
    except Exception as error:
        report.update({'status': 'failed', 'error_type': type(error).__name__, 'detail': str(error),
                       'failure_locations': [{'file': Path(frame.filename).name, 'line': frame.lineno}
                                             for frame in traceback.extract_tb(error.__traceback__)]})
        write(path, json_bytes(report))
        print(json.dumps({'status': 'failed', 'error_type': type(error).__name__, 'evidence': str(path)}), flush=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
