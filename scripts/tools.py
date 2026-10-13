#!/usr/bin/env python3
"""Install fixed helper tools in a project and verify actual CLI/MCP capabilities."""
import argparse
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import threading
import urllib.request

from personal import LIBRARY, detect, digest, json_bytes, load, safe, stamp, write
import stack_definitions
from mcp_stdio import MCPClient


class ToolCommandError(RuntimeError):
    def __init__(self, returncode, message):
        super().__init__(message)
        self.returncode = returncode


def run(project, command, label, env=None, timeout=600):
    evidence = safe(project, '.trellis/personal/evidence/' + stamp() + '-' + label)
    evidence.parent.mkdir(parents=True, exist_ok=True)
    handlers = {}
    process = None
    try:
        child_env = dict(os.environ if env is None else env, PWD=str(Path(project).resolve()))
        process = subprocess.Popen(command, cwd=project, env=child_env, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
        if threading.current_thread() is threading.main_thread():
            def interrupt(signum, _frame):
                if process.poll() is None:
                    os.killpg(process.pid, signum)
                raise KeyboardInterrupt
            for signum in [signal.SIGINT, signal.SIGTERM]:
                handlers[signum] = signal.signal(signum, interrupt)
        stdout, stderr = process.communicate(timeout=timeout)
        output = stdout + stderr
        write(evidence.with_suffix('.log'), output)
        if process.returncode:
            raise ToolCommandError(process.returncode, label + ' exit=' + str(process.returncode) + '; log=' + str(evidence.with_suffix('.log')))
        return stdout.decode(errors='replace')
    except subprocess.TimeoutExpired as error:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate(timeout=3)
        write(evidence.with_suffix('.log'), stdout + stderr)
        raise RuntimeError(label + ' timed out; inspect ' + str(evidence.with_suffix('.log'))) from error
    except BaseException:
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                stdout, stderr = process.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                stdout, stderr = process.communicate(timeout=3)
            write(evidence.with_suffix('.log'), stdout + stderr)
        raise
    finally:
        for signum, handler in handlers.items():
            signal.signal(signum, handler)


def fetch(url, destination):
    request = urllib.request.Request(url, headers={'User-Agent': 'personal-trellis-library/1.0'})
    with urllib.request.urlopen(request, timeout=60) as response:
        with open(destination, 'wb') as output:
            shutil.copyfileobj(response, output)


def model_endpoint_ready(project, uri):
    if not uri.startswith('hf:'):
        return Path(uri).is_file()
    owner, repo, filename = uri[3:].split('/', 2)
    url = 'https://huggingface.co/' + owner + '/' + repo + '/resolve/main/' + filename
    code = ('import sys,urllib.request; request=urllib.request.Request(sys.argv[1],method="HEAD"); '
            'response=urllib.request.urlopen(request,timeout=15); '
            'sys.exit(0 if response.status==200 else 1)')
    try:
        # Socket timeouts do not bound DNS/redirects. The subprocess deadline does.
        run(project, [sys.executable,'-c',code,url], 'qmd-model-endpoint', timeout=20)
        return True
    except (RuntimeError, OSError, ValueError):
        return False


def npm_tool(project, row, force_local=False):
    existing = shutil.which(row['bin'])
    if existing and not force_local:
        try:
            version = run(project, [existing, '--version'], row['bin'] + '-existing-version', timeout=20)
            if row['version'] in version:
                return Path(existing).resolve(), 'reused'
        except RuntimeError:
            pass
    prefix = safe(project, '.trellis/personal/tools/npm')
    installed = prefix / 'bin' / row['bin']
    metadata = prefix / 'lib/node_modules' / row['package'] / 'package.json'
    if installed.exists() and metadata.exists() and load(metadata)['version'] == row['version']:
        return installed, 'reused'
    node, npm = shutil.which('node'), shutil.which('npm')
    if not node or not npm:
        raise RuntimeError('A separate compatible Node/npm tool runtime is required; application runtime unchanged')
    node_version = run(project, [node, '--version'], 'tool-node-version', timeout=20).strip().lstrip('v')
    required = tuple(int(part) for part in row.get('node', '>=22.0.0').removeprefix('>=').split('.'))
    actual = tuple(int(part) for part in node_version.split('.')[:3])
    if actual < required:
        raise RuntimeError('Helper Node runtime is too old; provide a compatible runtime without changing application pins')
    command = [npm, 'install', '-g', '--prefix', str(prefix), '--save-exact', '--no-audit', '--no-fund',
               '--registry', 'https://registry.npmjs.org', '--cache', str(safe(project, '.trellis/personal/cache/npm')),
               '--logs-max=0', row['package'] + '@' + row['version']]
    if row.get('install_ignore_scripts'):
        command.insert(2, '--ignore-scripts')
    run(project, command, row['bin'] + '-install', timeout=900)
    if not installed.exists() or load(metadata)['version'] != row['version']:
        raise RuntimeError('Package installation did not provide the expected identity/version')
    return installed, 'installed'


def rtk_tool(project, row, force_local=False):
    existing = shutil.which('rtk')
    if existing and not force_local:
        try:
            version = run(project, [existing, '--version'], 'rtk-existing-version', timeout=20)
            run(project, [existing, 'gain'], 'rtk-existing-identity', timeout=20)
            if row['version'] in version:
                return Path(existing).resolve(), 'reused'
        except RuntimeError:
            pass
    binary = safe(project, '.trellis/personal/tools/bin/rtk')
    if binary.exists():
        version = run(project, [str(binary), '--version'], 'rtk-local-version', timeout=20)
        run(project, [str(binary), 'gain'], 'rtk-local-identity', timeout=20)
        if row['version'] in version:
            return binary, 'reused'
        raise RuntimeError('Existing project-local RTK differs from the locked version; explicit upgrade required')
    machine = platform.machine().lower()
    targets = {('Darwin','arm64'):'aarch64-apple-darwin', ('Darwin','aarch64'):'aarch64-apple-darwin',
               ('Linux','x86_64'):'x86_64-unknown-linux-musl', ('Linux','aarch64'):'aarch64-unknown-linux-gnu'}
    target = targets.get((platform.system(), machine))
    if not target:
        raise RuntimeError('RTK release adapter not verified for this host')
    archive_name = 'rtk-' + target + '.tar.gz'
    cache = safe(project, '.trellis/personal/cache/rtk')
    cache.mkdir(parents=True, exist_ok=True)
    archive, checksums = cache / archive_name, cache / 'checksums.txt'
    url = 'https://github.com/rtk-ai/rtk/releases/download/v' + row['version'] + '/'
    fetch(url + archive_name, archive)
    fetch(url + 'checksums.txt', checksums)
    matches = re.findall(r'^([0-9a-fA-F]{64})\s+\*?' + re.escape(archive_name) + r'\s*$', checksums.read_text(), re.M)
    if len(matches) != 1 or digest(archive.read_bytes()) != matches[0].lower():
        raise RuntimeError('Official RTK archive SHA-256 mismatch or missing checksum')
    with tarfile.open(archive) as contents:
        candidates = [member for member in contents.getmembers() if Path(member.name).name == 'rtk' and member.isfile()]
        if len(candidates) != 1:
            raise RuntimeError('Unexpected RTK archive layout')
        with contents.extractfile(candidates[0]) as source:
            write(binary, source.read())
    binary.chmod(0o755)
    run(project, [str(binary), '--version'], 'rtk-installed-version', timeout=20)
    run(project, [str(binary), 'gain'], 'rtk-installed-identity', timeout=20)
    return binary, 'installed'


def merge_codex(project, servers):
    path = safe(project, '.codex/config.toml')
    old = path.read_text() if path.exists() else ''
    body = old
    conflicts = []
    for name, config in servers.items():
        header = '[mcp_servers.' + name + ']'
        block = header + '\n'
        for key, value in config.items():
            block += key + ' = ' + toml_value(value) + '\n'
        # Modify no pre-existing server, including a personal server changed by the user.
        pattern = r'^\[mcp_servers\.' + re.escape(name) + r'\]\s*\n(?:(?!^\[).*(?:\n|$))*'
        match = re.search(pattern, body, re.M)
        if match:
            if match.group(0).strip() != block.strip():
                candidate = safe(project, '.trellis/personal/config-candidates/' + name + '.toml')
                write(candidate, block.encode())
                conflicts.append({'server': name, 'candidate': str(candidate.relative_to(project))})
            continue
        body = body.rstrip() + '\n\n' + block
    if body != old:
        if path.exists():
            write(safe(project, '.trellis/personal/backups/' + stamp() + '-codex-config.toml'), old.encode())
        write(path, body.encode())
    return {'status': 'conflicts' if conflicts else 'configured', 'conflicts': conflicts,
            'client_loaded': 'pending_actual_client_session'}


def toml_value(value):
    if isinstance(value, dict):
        return '{ ' + ', '.join(json.dumps(key) + ' = ' + toml_value(item)
                               for key, item in value.items()) + ' }'
    return json.dumps(value, ensure_ascii=False)


def qmd_environment(project):
    project = Path(project).resolve()
    return dict(os.environ, PWD=str(project), QMD_CONFIG_DIR=str(safe(project, '.qmd')),
                INDEX_PATH=str(safe(project, '.qmd/index.sqlite')),
                XDG_CACHE_HOME=str(safe(project, '.trellis/personal/cache')))


def qmd_config(project, binary, embedding=None):
    package = next((parent for parent in Path(binary).resolve().parents
                    if (parent / 'package.json').is_file() and
                    load(parent / 'package.json').get('name') == '@tobilu/qmd'), None)
    if not package:
        raise RuntimeError('Cannot identify locked QMD package configuration API')
    config_path = next((safe(project, '.qmd/' + name) for name in ['index.yaml', 'index.yml']
                        if safe(project, '.qmd/' + name).exists()), None)
    if config_path is None:
        raise RuntimeError('QMD configuration was not initialized')
    # Use the package's own YAML reader/writer. Never approve checkout hooks or
    # outside collections as a side effect of choosing the known embedding model.
    code = '''
import {pathToFileURL} from 'node:url';
const [packageRoot, configPath, projectRoot, desired] = process.argv.slice(1);
const api = await import(pathToFileURL(packageRoot + '/dist/collections.js').href);
const trust = await import(pathToFileURL(packageRoot + '/dist/trust.js').href);
api.setConfigSource({configPath});
const config = api.loadConfig();
for (const [name, collection] of Object.entries(config.collections || {})) {
 if (collection.update || !trust.isCollectionPathInsideProject(configPath, collection.path))
  throw new Error('Existing QMD hooks/outside collections require separate review: ' + name);
}
for (const [name, relative] of [['personal-specs','/.trellis/spec'],['personal-templates','/.trellis/personal/templates']]) {
 const collection = config.collections[name];
 if (collection && collection.path !== projectRoot + relative)
  throw new Error('Existing QMD collection name has a different owner: ' + name);
}
if (desired) {
 const builtins = (await import(pathToFileURL(packageRoot + '/dist/llm.js').href)).resolveModels();
 for (const [key, uri] of Object.entries(config.models || {}))
  if (uri !== builtins[key] && !(key === 'embed' && uri === desired))
   throw new Error('Existing custom QMD model requires explicit adaptation');
 config.models = {...config.models, embed:desired};
 api.saveConfig(config);
}
console.log(JSON.stringify({path:configPath,models:config.models,collections:config.collections}));
'''
    if embedding:
        write(safe(project, '.trellis/personal/backups/' + stamp() + '-qmd-config.yml'), config_path.read_bytes())
    return json.loads(run(project, [shutil.which('node'), '--input-type=module', '-e', code,
                                   str(package), str(config_path), str(project), embedding or ''],
                          'qmd-config-audit', env=qmd_environment(project), timeout=30))


def probe(project, command, label, symbol=None, env=None):
    log = safe(project, '.trellis/personal/evidence/' + stamp() + '-' + label + '-mcp.log')
    with MCPClient(command, project, log, env=env) as client:
        initialized = client.initialize(project)
        tools = client.tools()
        status = next((tool for tool in tools if tool['name'].endswith('status')), None)
        result = client.call(status['name']) if status else None
        search = None
        if symbol:
            tool = next((tool for tool in tools if tool['name'].endswith('search') and
                         'query' in tool.get('inputSchema',{}).get('properties',{})), None)
            if not tool:
                raise RuntimeError('Locked server does not expose expected representative-search schema')
            search = client.call(tool['name'],{'query':symbol})
            if symbol not in json.dumps(search):
                raise RuntimeError('Representative source symbol was not returned')
        return {'status': 'passed', 'server': initialized['serverInfo'],
                'protocol': initialized['protocolVersion'],
                'tools': [{'name':tool['name'],'parameters':list(tool.get('inputSchema',{}).get('properties',{}))} for tool in tools],
                'status_call': result, 'representative_search':search,
                'scope': 'stdio handshake/status' + (' and actual source symbol search' if symbol else '; source search not yet verified')}


def initialize(project, tool_names, force_local=False, models=False, symbol=None):
    lock = load(LIBRARY / 'tools.lock.json')
    state_path = safe(project, '.trellis/personal/tools-state.json')
    previous = load(state_path) if state_path.exists() else {}
    results, servers = {}, {}
    for name in tool_names:
        row = lock['tools'][name]
        result = {'version': row['version'], 'source': row['source']}
        try:
            if row.get('capability') == 'ui-design':
                from ui_tools import initialize_provider
                result.update(initialize_provider(project, name, row, force_local))
                results[name] = result
                write(state_path, json_bytes({**previous, **results}))
                print(json.dumps({'tool': name, 'status': result['status'],
                                  'installation': result.get('installation')}, ensure_ascii=False), flush=True)
                continue
            binary, installed = rtk_tool(project,row,force_local) if name == 'rtk' else npm_tool(project,row,force_local)
            result.update({'installation': installed, 'binary': str(binary)})
            if name == 'codegraph':
                if not any((project / '.codegraph').glob('*.db')):
                    run(project,[str(binary),'init','-i',str(project)],'codegraph-init')
                else:
                    run(project,[str(binary),'sync',str(project)],'codegraph-sync')
                run(project,[str(binary),'status',str(project)],'codegraph-index-status',timeout=30)
                command=[str(binary),'serve','--mcp','--path',str(project),'--no-watch']
                result['mcp']=probe(project,command,name,symbol)
                servers['personal_codegraph']={'command':str(binary),'args':command[1:],'cwd':str(project),
                                              'startup_timeout_sec':30,'tool_timeout_sec':30}
            elif name == 'qmd':
                qenv = qmd_environment(project)
                if not any((project / '.qmd' / name).exists() for name in ['index.yml', 'index.yaml']):
                    run(project,[str(binary),'init'],'qmd-init',env=qenv,timeout=60)
                index_path = safe(project, '.qmd/index.sqlite')
                if not index_path.is_file():
                    raise RuntimeError('QMD did not initialize the selected project-local index')
                qmd_config(project, binary)
                for collection,path in [('personal-specs',project/'.trellis/spec'),('personal-templates',project/'.trellis/personal/templates')]:
                    if not path.exists():
                        continue
                    listed=run(project,[str(binary),'collection','list'],'qmd-collections',env=qenv,timeout=30)
                    if collection not in listed:
                        run(project,[str(binary),'collection','add',str(path),'--name',collection,'--mask','**/*.md'],collection+'-add',env=qenv,timeout=120)
                run(project,[str(binary),'update'],'qmd-index-update',env=qenv,timeout=180)
                status_output = run(project,[str(binary),'status'],'qmd-index-location',env=qenv,timeout=30)
                if str(index_path) not in status_output:
                    raise RuntimeError('QMD actual index location differs from the selected project')
                result['index'] = str(index_path)
                keyword=run(project,[str(binary),'search','CodeGraph','-c','personal-specs','--json','-n','3'],'qmd-keyword',env=qenv,timeout=30)
                if not json.loads(keyword):
                    raise RuntimeError('QMD representative keyword returned no actual document hit')
                result['keyword_evidence']=keyword
                result['models']='pending' if not models else 'requested'
                if models:
                    embedding = row['embedding_model']
                    result['model_config'] = qmd_config(project, binary, embedding)
                    run(project,[str(binary),'trust'],'qmd-reviewed-model-trust',env=qenv,timeout=30)
                    cached = safe(project, '.trellis/personal/cache/qmd/models')
                    available = any(cached.glob('*' + embedding.rsplit('/',1)[-1]))
                    if not available and not model_endpoint_ready(project, embedding):
                        result['models']='unavailable_network'
                        result['model_error']='Public model endpoint unavailable within 20s; keyword/MCP remain usable'
                    else:
                        run(project,[str(binary),'embed'],'qmd-multilingual-embed',env=qenv,timeout=1200)
                        semantic = run(project,[str(binary),'vsearch','先设计再开发 文档一致性',
                                               '-c','personal-specs','--json','-n','3'],
                                       'qmd-chinese-vector',env=qenv,timeout=120)
                        if not json.loads(semantic):
                            raise RuntimeError('Chinese semantic query returned no indexed rule')
                        result['semantic_evidence'] = semantic
                        result['models']='embedding_ready_rerank_separate'
                command=[str(binary),'mcp']
                result['mcp']=probe(project,command,name,env=qenv)
                servers['personal_qmd']={'command':str(binary),'args':['mcp'],'cwd':str(project),
                                        'env':{key:qenv[key] for key in ['PWD','QMD_CONFIG_DIR','INDEX_PATH','XDG_CACHE_HOME']},
                                        'enabled_tools':['query','get','multi_get','status'],'startup_timeout_sec':60}
            elif name == 'rtk':
                result['identity_evidence']=run(project,[str(binary),'gain'],'rtk-gain',timeout=30)
                result['invocation']='explicit CLI; automatic hook activation not claimed'
            else:
                result['connection']='pending_project_credentials_and_actual_query'
            result['status']='installed_and_probed' if name in {'codegraph','qmd'} else 'installed'
        except (RuntimeError, OSError, ValueError) as error:
            result['status']='failed'
            result['error']=str(error)
        results[name]=result
        write(state_path,json_bytes({**previous,**results}))
        print(json.dumps({'tool':name,'status':result['status'],'installation':result.get('installation'),
                          'error':result.get('error')},ensure_ascii=False),flush=True)
    config=merge_codex(project,servers) if servers else {'status':'no_verified_server_to_configure'}
    pending = ['actual_current_client_load'] if servers else []
    pending += [name+':failed' for name,row in results.items() if row['status']=='failed']
    pending += [name+':local_skill_conflicts' for name,row in results.items() if row['status']=='conflicts']
    if any(row.get('capability') == 'ui-design' and row.get('status') == 'installed_and_probed'
           for row in results.values()):
        pending.append('ui:actual_client_auto_selection_not_observed')
    if 'qmd' in results and results['qmd'].get('models') in {'pending','unavailable_network'}:
        pending.append('qmd:semantic_model_not_prepared')
    if 'dbhub' in results:
        pending.append('database:connection_requires_database_adapter')
    if config.get('conflicts'):
        pending.append('client_config:conflicts')
    report={'tools':results,'codex':config,'detected':detect(project),
            'overall_complete':not pending,'pending':pending}
    write(safe(project,'.trellis/personal/tool-report.json'),json_bytes(report))
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,required=True)
    parser.add_argument('--tools',nargs='+',choices=['codegraph','rtk','qmd','dbhub','impeccable','ui-ux-pro-max'])
    parser.add_argument('--ui',action='store_true',help='Declare UI capability when it cannot be detected yet')
    parser.add_argument('--force-local',action='store_true')
    parser.add_argument('--models',action='store_true')
    parser.add_argument('--probe-symbol')
    args=parser.parse_args()
    project=args.project.resolve()
    project.mkdir(parents=True,exist_ok=True)
    default_names, route = default_tools(project, args.ui)
    names=args.tools or default_names
    report=initialize(project,names,args.force_local,args.models,args.probe_symbol)
    report['database_route'] = route
    if args.tools is None and route['state'] == 'provider_selection_pending':
        report['pending'].append('database:compatible_provider_selection_pending')
        report['overall_complete'] = False
    write(safe(project,'.trellis/personal/tool-report.json'),json_bytes(report))
    if any(row['status'] in {'failed','conflicts'} for row in report['tools'].values()):
        return 1
    return 2 if (args.tools is None and route['state'] == 'provider_selection_pending' or
                 args.models and report['tools'].get('qmd',{}).get('models')=='unavailable_network') else 0


def default_tools(project, declared_ui=False):
    definitions = stack_definitions.load(LIBRARY)
    detected = detect(project)
    state = safe(project, '.trellis/personal/install.json')
    installed = load(state) if state.exists() else {}
    stacks = set(detected['stacks']) | set(detected['databases']) | set(installed.get('selected_stacks', []))
    capabilities = set(installed.get('selected_capabilities', [])) | set(stack_definitions.capabilities(definitions, stacks))
    route = stack_definitions.database_route(definitions, stacks, 'database' in capabilities)
    names = ['codegraph', 'rtk', 'qmd']
    if route['provider']:
        names.append(route['provider'])
    if declared_ui or 'ui' in capabilities:
        names += ['impeccable', 'ui-ux-pro-max']
    return names, route


def ui_tools_required(project, declared=False):
    names, _ = default_tools(project, declared)
    return 'impeccable' in names


if __name__=='__main__':
    sys.exit(main())
