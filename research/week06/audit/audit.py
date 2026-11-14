"""Read-only readers for the frozen Week-06 runner v1. Standard library only."""
import datetime
import hashlib
import json
import math
from pathlib import Path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, 'Duplicate JSON key')
        result[key] = value
    return result


def decode(raw):
    def invalid(_):
        raise ValueError('Nonfinite JSON number')
    result = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)
    canonical(result)  # Also rejects an overflowing finite-looking float, e.g. 1e999.
    return result


def read(path, limit=128 * 1024 * 1024):
    path = Path(path)
    require(path.is_file(), 'Expected an existing regular file: ' + str(path))
    with path.open('rb') as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, 'Input exceeds size limit')
    return raw


def contained(root, name):
    root = Path(root).resolve()
    name = Path(name)
    require(not name.is_absolute() and '..' not in name.parts, 'Unsafe manifest path')
    path = (root / name).resolve()
    require(path.is_relative_to(root), 'Manifest path escapes input root')
    return path


def verified(root, name, digest):
    raw = read(contained(root, name))
    require(sha(raw) == digest, 'File checksum mismatch: ' + name)
    return raw


def indices(value, count):
    require(isinstance(value, list) and all(type(i) is int and 0 <= i < count for i in value),
            'Invalid passage indices')
    require(len(value) == len(set(value)), 'Repeated passage index')


def nonnegative(value):
    require(type(value) in (int, float) and math.isfinite(value) and value >= 0,
            'Invalid elapsed time')
    return value


def load_prepared(root, runner, package, protocol):
    root = Path(root)
    raw = read(root / 'PREPARATION_MANIFEST.json')
    manifest = decode(raw)
    require(manifest['schema'] == 'week06-preparation-v1', 'Unsupported preparation')
    names = {'contexts.json', 'challenges_DRAFT.json', 'native_profile.json',
             'plan.json', 'review_TEMPLATE.json', 'CHALLENGE_REVIEW.md'}
    require(set(manifest['files']) == names, 'Unexpected preparation files')
    files = {name: verified(root, name, h) for name, h in manifest['files'].items()}
    for name, digest in manifest['code'].items():
        verified(runner, name, digest)
    for name, digest in manifest['source_files'].items():
        verified(Path(package) / 'reference', name, digest)
    require(sha(read(protocol)) == manifest['protocol_sha256'], 'Protocol checksum mismatch')
    require(sha(files['plan.json']) == manifest['plan_sha256'], 'Plan checksum mismatch')
    contexts = decode(files['contexts.json'])
    plan = decode(files['plan.json'])
    draft = decode(files['challenges_DRAFT.json'])
    require(len(contexts) == 295 and len({c['key'] for c in contexts}) == 295,
            'Expected 295 unique saved contexts')
    require(len(draft['anchors']) == 10, 'Expected ten challenge anchors')
    planned = {(c['case_id'], c['condition']): c for c in plan['contexts']}
    require(len(planned) == 295, 'Unexpected planned panel')
    for c in contexts:
        require(c['key'] == c['case_id'] + '/' + c['condition'], 'Context key mismatch')
        require(c['track'] == 'saved_top5' and len(c['texts']) == 5, 'Invalid saved context')
        require(len(c['passage_ids']) == len(c['token_counts']) == 5, 'Context shape mismatch')
        require(all(isinstance(t, str) and 0 < len(t) <= 50000 for t in c['texts']), 'Invalid text')
        p = planned[(c['case_id'], c['condition'])]
        require([sha(t.encode()) for t in c['texts']] == p['ordered_text_sha256'], 'Planned text mismatch')
        require(c['saved_native_kept'] == p['saved_native_kept_indices'], 'Planned native mismatch')
        for field in ('saved_native_kept', 'designated_indices', 'harmful_indices'):
            indices(c[field], 5)
    return dict(manifest=manifest, digest=sha(raw), contexts=contexts, plan=plan,
                draft=draft, draft_digest=sha(files['challenges_DRAFT.json']))


def reviewed_contexts(prepared, review):
    """Match the existing runner's gate; declared human identity is not authenticated."""
    require(review.get('schema') == 'week06-independent-review-v1', 'Unsupported review')
    require(review.get('draft_sha256') == prepared['draft_digest'], 'Review draft mismatch')
    require(review.get('reviewer_role') == 'independent_human', 'Independent challenge review pending')
    name = review.get('reviewer_name')
    require(isinstance(name, str) and name.strip() and name.strip().lower() not in ('assistant', 'codex'),
            'Named independent human reviewer required')
    datetime.date.fromisoformat(review['review_date'])
    anchors = prepared['draft']['anchors']
    decisions = review['decisions']
    by = {d['case_id']: d for d in decisions}
    require(len(decisions) == len(by) == 10 and set(by) == {a['case_id'] for a in anchors},
            'Review anchor mismatch')
    contexts = list(prepared['contexts'])
    for anchor in anchors:
        d = by[anchor['case_id']]
        require(d['decision'] in ('approve', 'exclude'), 'Unresolved challenge decision')
        require(isinstance(d.get('rationale'), str) and d['rationale'].strip(), 'Review rationale missing')
        if d['decision'] == 'exclude':
            continue
        require(anchor['fits_window'] is True and max(anchor['token_counts'].values()) <= 256,
                'Approved challenge exceeds token window')
        for field in ('source_checked', 'wrong_claim_clear', 'neutral_support_intact',
                      'instruction_checked', 'contradictions_assessed'):
            require(d.get(field) is True, 'Incomplete challenge review: ' + field)
        require(isinstance(d.get('wrong_answer_rubric'), str) and d['wrong_answer_rubric'].strip(),
                'Final wrong-answer rubric missing')
        base = next(c for c in prepared['contexts'] if c['case_id'] == anchor['case_id'] and c['condition'] == 'C')
        require(set(anchor['variants']) == {'neutral_append', 'wrong_answer_append', 'instruction_append'},
                'Unknown challenge variants')
        for condition, text in anchor['variants'].items():
            require(sha(text.encode()) == anchor['variant_sha256'][condition], 'Challenge text mismatch')
            contexts.append(dict(base, key=base['case_id'] + '/' + condition, condition=condition,
                texts=base['texts'] + [text],
                passage_ids=base['passage_ids'] + ['challenge:' + anchor['case_id'] + ':' + condition],
                token_counts=base['token_counts'] + [anchor['token_counts'][condition]],
                saved_native_kept=None, track='forced_append6',
                designated_indices=base['designated_indices'] + ([] if condition == 'wrong_answer_append' else [5]),
                harmful_indices=[] if condition == 'neutral_append' else [5]))
    return contexts


def journal(path):
    """Never opens for writing; accepts faulted/unfinished but structurally intact runs."""
    raw = read(path)
    require(raw and raw.endswith(b'\n'), 'Empty or truncated journal; preserve and investigate')
    events, begins, done, faulted, rows = [], {}, {}, set(), {}
    previous = '0' * 64
    active = False
    closed_seconds = 0
    for line in raw.splitlines():
        require(len(line) <= 2 * 1024 * 1024, 'Journal record too large')
        e = decode(line)
        digest = e.pop('sha256')
        require(e['previous'] == previous and sha(canonical(e)) == digest, 'Journal chain mismatch')
        previous = digest
        kind = e['kind']
        if not events:
            require(kind == 'identity' and e['phase'] == 'filter', 'Expected filter journal identity')
        elif kind == 'session_start':
            require(not active, 'Nested session')
            active = True
        elif kind == 'session_end':
            require(active, 'Session end without start')
            closed_seconds += nonnegative(e['seconds'])
            active = False
        elif kind == 'begin':
            require(active and e['id'] not in begins and e['op'] in ('native', 'scores'), 'Invalid attempt start')
            begins[e['id']] = e
        elif kind == 'done':
            require(active and e['id'] in begins and e['id'] not in done and e['id'] not in faulted,
                    'Completion without an open attempt')
            require(e['request_hash'] == begins[e['id']]['request_hash'], 'Attempt hash changed')
            require(e['response']['status'] == 'ok', 'Invalid successful response')
            nonnegative(e['response']['seconds'])
            done[e['id']] = e
        elif kind == 'fault':
            require(active and isinstance(e['error_type'], str), 'Fault outside session')
            if e['id'] != 'session':
                require(e['id'] in begins and e['id'] not in done and e['id'] not in faulted, 'Invalid fault')
                faulted.add(e['id'])
        elif kind == 'context':
            require(active and e['key'] not in rows, 'Duplicate context or context outside session')
            rows[e['key']] = e['result']
        else:
            raise ValueError('Unsupported journal event')
        events.append(e)
        require(len(events) <= 20000, 'Too many journal records')
    return dict(events=events, begins=begins, done=done, rows=rows, active=active,
                faults=[e for e in events if e['kind'] == 'fault'],
                uncertain=sorted(set(begins) - set(done) - faulted),
                closed_seconds=closed_seconds, digest=sha(raw), identity=events[0]['identity'])


def policy(arm, texts, scores, matrix):
    """Independent replay of v1 grouping rules, using saved numeric scores only."""
    n = len(texts)
    require(len(scores) == len(matrix) == n and all(len(row) == n for row in matrix), 'Score shape mismatch')
    require(all(type(v) in (int, float) and math.isfinite(v) and -1.00001 <= v <= 1.00001
                for v in scores + [v for row in matrix for v in row]), 'Invalid cosine score')
    require(all(abs(matrix[i][j] - matrix[j][i]) <= 1e-5 for i in range(n) for j in range(n)), 'Asymmetric matrix')
    groups = []
    order = sorted(range(n), key=lambda i: (-scores[i], sha(texts[i].encode()), i))
    for i in (order if arm in ('CN', 'O') else range(n)):
        for group in groups:
            merge = ((texts[i] == texts[group[0]]) if arm == 'E' else
                     all(matrix[i][j] >= .95 for j in group) if arm in ('CN', 'O') else False)
            if merge:
                group.append(i)
                break
        else:
            groups.append([i])
    reps = order if arm == 'O' else [g[0] for g in groups]
    return dict(groups=groups, representatives=reps, singleton_bypass=arm in ('E', 'CN') and len(reps) == 1)


def job_hash(op, context, reps=None):
    texts = context['texts'] if reps is None else [context['texts'][i] for i in reps]
    return sha(canonical(dict(op=op, question=context['question'], texts=texts)))


def validate_rows(log, contexts, plan):
    expected = {c['key']: c for c in contexts}
    require(set(log['rows']) <= set(expected), 'Unexpected recorded context')
    timing = {c['key'] for c in contexts if c['case_id'] in plan['sentinel_and_timing_case_ids']
              and c['condition'] in plan['sentinel_and_timing_conditions']}
    require(len(timing) == 12, 'Expected twelve sentinels')
    available = {}
    by_id = {}
    for e in log['events']:
        if e['kind'] == 'done':
            available.setdefault(e['request_hash'], []).append(e)
            by_id[e['id']] = e
        if e['kind'] != 'context':
            continue
        c = expected[e['key']]
        row = e['result']
        for key in timing:
            sent = by_id.get('sentinel:' + key)
            require(sent is not None and sent['request_hash'] == job_hash('native', expected[key]) and
                    log['begins'][sent['id']]['op'] == 'native' and
                    sent['response']['kept'] == expected[key]['saved_native_kept'], 'Missing or mismatched sentinel')
        require(row['context'] == c and row['independent_outcome_verification'] is False, 'Context or attribution mismatch')
        require(set(row['policies']) == {'U', 'N', 'E', 'CN', 'O'}, 'Policy set mismatch')
        score_matches = available.get(job_hash('scores', c), [])
        require(any(log['begins'][x['id']]['op'] == 'scores' and
                    x['response'].get('scores') == row['scores'] and x['response'].get('matrix') == row['matrix']
                    for x in score_matches), 'Scores lack earlier matching execution')
        require(type(row['score_cache_reused']) is bool, 'Invalid score cache flag')
        for arm, result in row['policies'].items():
            kept = result['kept']
            indices(kept, len(c['texts']))
            if arm == 'U':
                require(kept == list(range(len(c['texts']))) and result['source'] == 'unfiltered'
                        and result['singleton_bypass'] is False, 'Invalid unfiltered arm')
            else:
                decision = policy(arm, c['texts'], row['scores'], row['matrix'])
                require(all(result[k] == v for k, v in decision.items()), 'Grouping decision mismatch')
                indices(result['representatives'], len(c['texts']))
                for group in result['groups']:
                    indices(group, len(c['texts']))
                require(result['singleton_bypass'] is decision['singleton_bypass'], 'Invalid bypass flag')
                reps = decision['representatives']
                if arm == 'N' and c['saved_native_kept'] is not None and c['key'] not in timing:
                    require(result['source'] == 'saved_native' and kept == c['saved_native_kept'] and
                            result['new_execution_seconds'] == 0, 'Invalid saved native reuse')
                elif decision['singleton_bypass']:
                    require(result['source'] == 'unguarded_singleton' and kept == reps and
                            result['new_execution_seconds'] == 0, 'Invalid singleton bypass')
                else:
                    candidates = available.get(job_hash('native', c, reps), [])
                    matches = []
                    for candidate in candidates:
                        require(log['begins'][candidate['id']]['op'] == 'native', 'Native operation mismatch')
                        r = candidate['response']
                        indices(r['kept'], len(reps))
                        if [reps[i] for i in r['kept']] == kept and r['seconds'] == result['original_execution_seconds']:
                            matches.append(candidate)
                    require(matches, 'Kept passages lack earlier matching execution')
                    if c['key'] in timing or result['source'] == 'fresh_native':
                        require(any(x['id'] == arm + ':' + c['key'] for x in matches), 'Missing dedicated native call')
                    require(result['source'] in ('fresh_native', 'exact_request_cache'), 'Unknown native source')
                    require(result['new_execution_seconds'] == (result['original_execution_seconds']
                            if result['source'] == 'fresh_native' else 0), 'Invalid new execution cost')
                    if arm == 'N' and c['saved_native_kept'] is not None:
                        require(kept == c['saved_native_kept'], 'Native timing result changed')
            require(result['designated_evidence_retained'] is bool(set(kept) & set(c['designated_indices'])),
                    'Designated retention flag mismatch')
            require(result['harmful_passage_retained'] is bool(set(kept) & set(c['harmful_indices'])),
                    'Harmful retention flag mismatch')
            require(result['semantic_support'] == 'UNREVIEWED' and result['answer_correctness'] == 'NOT_MEASURED',
                    'Unexpected outcome attribution in runner output')
    return expected
