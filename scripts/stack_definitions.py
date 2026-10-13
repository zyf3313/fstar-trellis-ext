"""Reviewed detection metadata; independent of Trellis native marketplace schema."""
import json
from pathlib import Path
import re

KINDS = {'feature', 'npm', 'python', 'maven', 'gradle', 'gradle-plugin',
         'go', 'cargo', 'composer', 'nuget', 'pub', 'swift-package', 'image'}


def load(root):
    path = Path(root) / 'stack-definitions.json'
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 1_000_000:
        raise ValueError('Stack definitions missing, linked or oversized')
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        raise ValueError('Unsupported stack definition schema')
    groups, ids = set(), set()
    if not isinstance(data.get('groups'), list) or not isinstance(data.get('stacks'), list):
        raise ValueError('Stack definitions require groups and stacks')
    for group in data['groups']:
        if (not isinstance(group, dict) or not isinstance(group.get('id'), str)
                or not re.fullmatch(r'[a-z][a-z0-9-]{0,63}', group['id'])
                or not isinstance(group.get('title_zh'), str) or not group['title_zh']):
            raise ValueError('Invalid stack group')
        if group['id'] in groups:
            raise ValueError('Duplicate stack group')
        groups.add(group['id'])
    for item in data['stacks']:
        if (not isinstance(item, dict) or not isinstance(item.get('id'), str)
                or not re.fullmatch(r'[a-z][a-z0-9-]{0,63}', item['id'])
                or item['id'] in ids or not isinstance(item.get('group'), str) or item['group'] not in groups
                or not all(isinstance(item.get(key), str) and item[key] for key in ('name', 'summary_zh', 'detection_zh'))):
            raise ValueError('Invalid or duplicate stack definition')
        ids.add(item['id'])
        if (not isinstance(item.get('capabilities', []), list)
                or any(not isinstance(capability, str) or capability not in {'ui', 'database'} for capability in item.get('capabilities', []))):
            raise ValueError('Invalid stack capabilities: ' + item['id'])
        if item.get('database_provider') not in (None, 'dbhub'):
            raise ValueError('Unknown database provider: ' + item['id'])
        if item.get('database_provider') and 'database' not in item.get('capabilities', []):
            raise ValueError('Database provider without database capability')
        if not isinstance(item.get('markers'), list):
            raise ValueError('Stack definition requires reviewed markers')
        for marker in item['markers']:
            if (not isinstance(marker, dict) or set(marker) - {'kind', 'names', 'prefixes', 'version'}
                    or not isinstance(marker.get('kind'), str) or marker['kind'] not in KINDS
                    or type(marker.get('version', True)) is not bool):
                raise ValueError('Invalid marker for ' + item['id'])
            names, prefixes = marker.get('names', []), marker.get('prefixes', [])
            if (not isinstance(names, list) or not isinstance(prefixes, list) or not (names or prefixes)
                    or any(not isinstance(name, str) or not name or len(name) > 200 for name in names + prefixes)):
                raise ValueError('Marker requires bounded exact names or reviewed prefixes')
    return data


def capabilities(data, stacks):
    return sorted({cap for item in data['stacks'] if item['id'] in stacks for cap in item.get('capabilities', [])})


def database_route(data, stacks, requested=False):
    engines = [item for item in data['stacks'] if item['id'] in stacks and 'database' in item.get('capabilities', [])]
    supported = sorted(item['id'] for item in engines if item.get('database_provider') == 'dbhub')
    pending = sorted(item['id'] for item in engines if not item.get('database_provider'))
    return {'provider': 'dbhub' if supported else None, 'supported_engines': supported,
            'pending_engines': pending, 'state': 'provider_selection_pending' if pending or requested and not engines
            else 'connection_pending' if supported else 'not_applicable'}


def apply(data, dependencies, row):
    """Each fact is a parsed manifest field, never arbitrary substring text."""
    row['detection_evidence'] = {}
    row['raw_versions'] = {}
    row['version_facts'] = {}
    row['databases'] = []
    for item in data['stacks']:
        matches = []
        for marker in item['markers']:
            for fact in dependencies:
                if (fact['kind'] == marker['kind'] and (fact['name'] in marker.get('names', [])
                        or any(fact['name'].startswith(prefix) for prefix in marker.get('prefixes', [])))):
                    matches.append((marker, fact))
        if not matches:
            continue
        if 'database' in item.get('capabilities', []):
            row['databases'].append(item['id'])
        else:
            row['stacks'].append(item['id'])
        row['detection_evidence'][item['id']] = [fact['origin'] for _, fact in matches]
        # Resolved facts are appended after declarations by parsers and win only within this manifest scope.
        for marker, fact in matches:
            if marker.get('version', True) and fact.get('version'):
                records = row['version_facts'].setdefault(item['id'], [])
                if ': resolved dependency ' in fact['origin']:
                    records[:] = [record for record in records
                                  if (record['kind'], record['name']) != (fact['kind'], fact['name'])]
                record = {'version': fact['version'], 'raw': fact.get('raw', fact['version']),
                          'evidence': fact['origin'], 'kind': fact['kind'], 'name': fact['name']}
                if record not in records:
                    records.append(record)
                row['versions'][item['id']] = fact['version']
                row['raw_versions'][item['id']] = fact.get('raw', fact['version'])
                row['version_evidence'][item['id']] = fact['origin']
    row['stacks'], row['databases'] = sorted(set(row['stacks'])), sorted(set(row['databases']))
    return row
