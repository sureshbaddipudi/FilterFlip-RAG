#!/usr/bin/env python3
"""Offline traceability/integrity checks. Never imports or launches the app/model."""
import argparse
import ast
import collections
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root, check_originals=False, check_release=False, check_package=False):
    errors = []
    checks = {}
    def require(condition, message):
        if not condition:
            errors.append(message)
    def read(name):
        return json.loads((root / (name + '.json')).read_text())
    def safe_child(base, relative):
        candidate = base / relative
        require(not Path(relative).is_absolute() and '..' not in Path(relative).parts,
                'Unsafe relative path: ' + relative)
        return candidate
    sources = read('SOURCE_MANIFEST')
    for name, entry in sources.items():
        path = safe_child(root / 'sources', name)
        require(path.is_file() and not path.is_symlink(), 'Missing/nonregular source: ' + name)
        if path.is_file():
            require(digest(path) == entry['sha256'], 'Source snapshot changed: ' + name)
        if check_originals:
            original = Path(entry['source'])
            require(original.is_file() and digest(original) == entry['sha256'],
                    'Original source missing/changed: ' + entry['source'])
    require(len(sources) == 53, 'Expected 53 named source snapshots')
    checks['source_snapshots'] = len(sources)
    checks['originals_compared'] = len(sources) if check_originals else 'not requested'
    actual_anchors = {}
    actual_tests = []
    for name in sources:
        if not name.endswith('.py'):
            continue
        symbols = {}
        tree = ast.parse((root / 'sources' / name).read_text())
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                symbols[node.name] = node.lineno
                if isinstance(node, ast.ClassDef):
                    for method in node.body:
                        if isinstance(method, ast.FunctionDef):
                            symbol = node.name + '.' + method.name
                            symbols[symbol] = method.lineno
                            if method.name.startswith('test_'):
                                actual_tests.append({'file': name, 'symbol': symbol, 'line': method.lineno})
        actual_anchors[name] = symbols
    require(read('CODE_ANCHORS') == actual_anchors, 'Code anchor catalog differs from parsed snapshots')
    require(read('TEST_CATALOG') == actual_tests, 'Test catalog differs from parsed snapshots')
    counts = collections.Counter(t['file'].split('/')[0] for t in actual_tests)
    require(counts == {'app': 42, 'task03': 19}, 'Expected separate 42 app / 19 Task-3 method catalogs')
    checks['existing_test_methods_catalogued_not_executed'] = dict(counts)
    controls, risks, evidence, rows = (read(n) for n in
        ['CONTROL_REGISTER', 'RISK_REGISTER', 'EVIDENCE_REGISTER', 'RISK_MAPPING'])
    ids = {}
    for name, records, expected in [('controls', controls, 12), ('risks', risks, 14), ('evidence', evidence, 23)]:
        keys = [x['id'] for x in records]
        require(len(keys) == expected and len(set(keys)) == expected, 'Duplicate/missing IDs in ' + name)
        ids[name] = set(keys)
        checks[name] = len(records)
    def links(record, field, target):
        for ref in record.get(field, []):
            require(ref in ids[target], record['id'] + ': unknown ' + field + ' ' + ref)
    for item in evidence:
        require(item['file'] in sources, item['id'] + ': evidence snapshot missing')
        require(bool(item.get('attribution_and_scope')) and bool(item.get('task04_action')),
                item['id'] + ': missing evidence scope')
    test_keys = {(t['file'], t['symbol']) for t in actual_tests}
    reference_count = 0
    for item in controls:
        links(item, 'evidence_ids', 'evidence')
        for field in ['requirement', 'implementation', 'residual_limit', 'legacy_namespace']:
            require(bool(item.get(field)), item['id'] + ': missing ' + field)
        for field in ['code', 'test_references']:
            require(bool(item[field]), item['id'] + ': empty ' + field)
            for ref in item[field]:
                reference_count += 1
                require(ref['symbol'] in actual_anchors.get(ref['file'], {}),
                        item['id'] + ': unresolved symbol ' + str(ref))
                if field == 'test_references':
                    require((ref['file'], ref['symbol']) in test_keys, item['id'] + ': reference is not a test method')
    checks['code_and_test_symbol_references'] = reference_count
    for item in risks:
        links(item, 'controls', 'controls'); links(item, 'evidence_ids', 'evidence')
        require(item.get('risk_acceptance') == 'not recorded by this mapping', item['id'] + ': invented acceptance')
        require(all(isinstance(t, int) and 1 <= t <= 13 for t in item['follow_up_tasks']), item['id'] + ': invalid follow-up task')
    expected = {'STRIDE': set('STRIDE')}
    expected.update({framework: {prefix + str(i).zfill(width) + ':' + year for i in range(1, 11)}
                     for framework, prefix, width, year in [('WEB', 'A', 2, '2025'), ('API', 'API', 1, '2023'),
                                                          ('LLM', 'LLM', 2, '2025'), ('ML', 'ML', 2, '2023')]})
    actual = collections.defaultdict(list)
    for item in rows:
        actual[item['framework']].append(item['id'])
        for field in ['title', 'applicability', 'scenario', 'controls', 'risk_ids', 'evidence_ids',
                      'remaining_gap', 'scoped_exclusion_or_reassessment_trigger', 'official_reference']:
            require(bool(item.get(field)), item['id'] + ': empty ' + field)
        require(item['status'] == 'applicability_mapped_not_category_certified', item['id'] + ': invalid certification status')
        require(item['official_reference'].startswith('https://'), item['id'] + ': missing official URL')
        links(item, 'controls', 'controls'); links(item, 'risk_ids', 'risks'); links(item, 'evidence_ids', 'evidence')
    require(set(actual) == set(expected), 'Missing/extra framework')
    for framework, wanted in expected.items():
        require(set(actual[framework]) == wanted and len(actual[framework]) == len(wanted),
                framework + ': missing/duplicate/unexpected category')
    checks['category_counts'] = {k: len(v) for k, v in actual.items()}
    standards = read('STANDARD_REFERENCES')
    require(len(standards) == 5 and any(x['id'] == 'ML' and 'draft' in x['edition'] for x in standards),
            'ML draft status missing')
    crosswalk = read('LEGACY_ID_CROSSWALK')
    require(len(crosswalk) == 10 and len({x['historical_id'] for x in crosswalk}) == 10, 'Legacy crosswalk incomplete')
    for item in crosswalk:
        require(item['historical_id'].startswith('W4-BACKLOG:SEC-'), 'Unqualified legacy ID')
        require(set(item['current_control_ids']) <= ids['controls'], 'Invalid legacy target')
    checks['qualified_historical_backlog_ids'] = len(crosswalk)
    for filename, count in [('app/validation/v2_1-tests-normal.log', 42), ('app/validation/v2_1-tests-optimized.log', 42),
                            ('task03/validation/tests_normal_final_v2.log', 19), ('task03/validation/tests_optimized_final_v2.log', 19)]:
        log = (root / 'sources' / filename).read_text()
        require('Ran ' + str(count) + ' tests' in log and '\nOK' in log, 'Unexpected recorded test summary: ' + filename)
    checks['recorded_test_log_summaries'] = '42 app normal/optimized; 19 Task-3 normal/optimized; not fresh Task-4 execution'
    current_status = json.loads((root / 'sources/Task03_status.json').read_text())
    require(current_status['unique_status_counts'] == {'ok': 60} and current_status['logical_status_counts'] == {'ok': 72},
            'Task-3 computational status differs')
    require(current_status['human_semantic_review'] == 'pending under task 7' and current_status['R110'] == 'uncertain unchanged',
            'Task-3 uncertainty/review status changed')
    if check_release:
        release_source = Path(sources['app/RELEASE_MANIFEST.json']['source'])
        release = json.loads(release_source.read_text())
        require(len(release) == 156, 'Expected 156 current app release entries')
        for filename, wanted in release.items():
            path = safe_child(release_source.parent, filename)
            require(path.is_file() and digest(path) == wanted, 'Current app release changed: ' + filename)
        checks['original_current_app_release_files_verified'] = len(release)
    else:
        checks['original_current_app_release_files_verified'] = 'not requested (portable check)'
    if check_package:
        package = read('SHA256_MANIFEST')
        actual_files = {str(f.relative_to(root)) for f in root.rglob('*') if f.is_file() and f != root / 'SHA256_MANIFEST.json'}
        require(set(package) == actual_files, 'Package manifest inventory differs')
        for filename, wanted in package.items():
            path = safe_child(root, filename)
            require(path.is_file() and digest(path) == wanted, 'Package member changed: ' + filename)
        checks['package_manifest_files'] = len(package)
    return {'status': 'FAIL' if errors else 'PASS', 'checked_at': datetime.now(timezone.utc).isoformat(),
            'task': 4, 'checks': checks, 'errors': errors,
            'scope': 'Offline structure, traceability and byte integrity only; no fresh security test/scanner/model inference or risk acceptance.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--check-originals', action='store_true', help='Read original absolute source paths on the authoring machine')
    parser.add_argument('--check-release', action='store_true', help='Read all 156 original app manifest entries on the authoring machine')
    parser.add_argument('--check-package', action='store_true', help='Check sealed package manifest without changing it')
    parser.add_argument('--write', action='store_true', help='Authoring only: save validation/MAPPING_CHECK.json before sealing')
    args = parser.parse_args()
    if args.write and args.check_package:
        parser.error('--write and --check-package cannot be combined')
    result = validate(args.root.resolve(), args.check_originals, args.check_release, args.check_package)
    if args.write:
        (args.root / 'validation/MAPPING_CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
