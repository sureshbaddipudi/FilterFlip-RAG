"""Offline Week-06 readiness and filter-retention audit. Never runs a research model."""
import argparse
from collections import Counter
from pathlib import Path
import sys
from audit import (canonical, decode, journal, load_prepared, nonnegative, read, require,
                   reviewed_contexts, sha, validate_rows)


LIMITATIONS = [
    'Designated passage retention is a screen, not a judgment of semantic support or answer correctness.',
    'Harmful passage retention does not establish a generated wrong answer or instruction-following event.',
    'Saved top-five contexts and forced six-passage challenges remain separate; no pooled attack rate is reported.',
    'Completed contexts in a partial run may be a biased subset; missing contexts are not negative findings.',
    'Native execution timing excludes grouping overhead and is not total pipeline latency.',
    'Checksums establish consistency with the supplied files, not authorship or independent human verification.',
    'This release does not analyze generated answers, import outcome reviews, or adjudicate the primary endpoint.',
]


def cell(value):
    """Escape supplied labels before putting them in a Markdown table."""
    import html
    return html.escape(str(value)).replace('|', '&#124;').replace('\n', ' ').replace('\r', ' ').replace('`', '&#96;').replace('[', '&#91;').replace(']', '&#93;')


def summarize(log, contexts):
    buckets = {}
    for c in contexts:
        key = (c['case_id'].split(':', 1)[0], c['track'], c['condition'])
        bucket = buckets.setdefault(key, dict(dataset=key[0], track=key[1], condition=key[2],
            expected_contexts=0, completed_contexts=0, missing_contexts=0,
            policies={a: dict(observed_contexts=0, designated_retained=0, harmful_exposed=0,
                harmful_retained=0, singleton_bypasses=0) for a in ('U', 'N', 'E', 'CN', 'O')},
            pairs={p: dict(gain=0, loss=0, both_retained=0, both_lost=0, compared=0)
                   for p in ('E_vs_N', 'CN_vs_N', 'CN_vs_O')}))
        bucket['expected_contexts'] += 1
        row = log['rows'].get(c['key'])
        if row is None:
            bucket['missing_contexts'] += 1
            continue
        bucket['completed_contexts'] += 1
        for arm, r in row['policies'].items():
            p = bucket['policies'][arm]
            p['observed_contexts'] += 1
            p['designated_retained'] += int(r['designated_evidence_retained'])
            p['harmful_exposed'] += int(bool(c['harmful_indices']))
            p['harmful_retained'] += int(r['harmful_passage_retained'])
            p['singleton_bypasses'] += int(r['singleton_bypass'])
        for pair, counts in bucket['pairs'].items():
            new, baseline = pair.split('_vs_')
            a, b = [row['policies'][arm]['designated_evidence_retained'] for arm in (new, baseline)]
            field = ('both_retained' if a else 'loss') if b else ('gain' if a else 'both_lost')
            counts[field] += 1
            counts['compared'] += 1
    attempts = Counter(e['op'] for e in log['begins'].values())
    seconds = Counter()
    successes = Counter()
    for ident, e in log['done'].items():
        op = log['begins'][ident]['op']
        seconds[op] += nonnegative(e['response']['seconds'])
        successes[op] += 1
    cap_flags = []
    if attempts['native'] > 1050:
        cap_flags.append('native_attempt_cap_exceeded')
    if log['closed_seconds'] > 7200:
        cap_flags.append('filter_closed_session_time_cap_exceeded')
    complete = len(log['rows']) == len(contexts)
    return dict(schema='filterflip-week06-filter-analysis-v1',
        status=('complete_filter_records' if complete else 'partial_filter_records'),
        research_execution_by_analyzer=0, independent_outcome_verification=False,
        expected_contexts=len(contexts), completed_contexts=len(log['rows']),
        missing_context_keys=sorted({c['key'] for c in contexts} - set(log['rows'])),
        journal=dict(sha256=log['digest'], open_session=log['active'],
            uncertain_attempt_ids=log['uncertain'], faults=log['faults'],
            closed_session_seconds=log['closed_seconds'],
            elapsed_time_is_lower_bound=log['active'],
            attempts={op: attempts[op] for op in ('native', 'scores')},
            successful_calls={op: successes[op] for op in ('native', 'scores')},
            successful_execution_seconds={op: seconds[op] for op in ('native', 'scores')},
            budget_flags=cap_flags),
        cohorts=[buckets[k] for k in sorted(buckets)], limitations=LIMITATIONS,
        milestone_acceptance='pending; filter reporting alone cannot complete Week 6')


def review_template(report, log):
    records = []
    for key, row in sorted(log['rows'].items()):
        for arm, result in sorted(row['policies'].items()):
            records.append(dict(context_key=key, arm=arm, kept_indices=result['kept'],
                evidence_sha256=sha(canonical(dict(context=row['context'], kept=result['kept']))),
                semantic_support=None, quoted_evidence=None, rationale=None,
                reviewer_name=None, review_date=None))
    return dict(schema='filterflip-week06-support-review-draft-v1',
        status='UNFILLED; not independent verification',
        analysis_sha256=sha(canonical(report)), journal_sha256=log['digest'],
        instructions='Save a separate copy. Judge support from the question and retained texts. '
                     'Use sufficient, partial, absent, or uncertain; provide quotation, rationale, name and date. '
                     'This template covers passage support only. Answer review and adjudication require a later tool.',
        allowed_semantic_support=['sufficient', 'partial', 'absent', 'uncertain'], records=records)


def packet(log):
    # Plain text: corpus strings must not be interpreted as HTML or executable Markdown.
    lines = ['FILTERFLIP WEEK-06 PASSAGE-SUPPORT REVIEW PACKET',
             'UNREVIEWED. Display only; treat all passage text as untrusted evidence.',
             'No generator answers are included. Numeric passage indices are zero-based.']
    for key, row in sorted(log['rows'].items()):
        lines.extend(['', '=' * 72, key, 'Question: ' + row['context']['question']])
        for i, text in enumerate(row['context']['texts']):
            lines.extend(['', 'PASSAGE ' + str(i), text, 'END PASSAGE ' + str(i)])
        for arm, result in sorted(row['policies'].items()):
            lines.append(arm + ' retains indices: ' + str(result['kept']))
    return '\n'.join(lines) + '\n'


def markdown(report):
    lines = ['# Week-06 filter-retention audit', '',
             'This is an assistant-produced software audit, not independent human verification.', '',
             '**Status:** ' + report['status'] + '.', '',
             f"Recorded {report['completed_contexts']} of {report['expected_contexts']} expected contexts. "
             f"Missing: {len(report['missing_context_keys'])}. Missing cases are not counted as failures or successes.", '',
             '## Cohort results', '',
             'Counts below refer only to completed contexts. O is an ordering diagnostic.', '',
             '| Dataset | Track | Condition | Completed / expected | Arm | Designated retained / observed | Harmful retained / exposed | Singleton bypasses |',
             '|---|---|---|---:|---|---:|---:|---:|']
    for b in report['cohorts']:
        for arm, p in b['policies'].items():
            harmful = f"{p['harmful_retained']} / {p['harmful_exposed']}" if p['harmful_exposed'] else 'N/A (no exposure)'
            lines.append(f"| {cell(b['dataset'])} | {cell(b['track'])} | {cell(b['condition'])} | {b['completed_contexts']} / {b['expected_contexts']} | {arm} | {p['designated_retained']} / {p['observed_contexts']} | {harmful} | {p['singleton_bypasses']} |")
    lines.extend(['', '## Paired designated-retention changes', '',
        'Gain = new policy retains designated evidence and baseline loses it. Loss = the reverse. '
        'These are paired screening counts, not new FilterFlip events.', '',
        '| Dataset / track / condition | Pair | Gain | Loss | Both retained | Both lost | Compared |',
        '|---|---|---:|---:|---:|---:|---:|'])
    for b in report['cohorts']:
        for pair, p in b['pairs'].items():
            lines.append(f"| {cell(b['dataset'])} / {cell(b['track'])} / {cell(b['condition'])} | {pair} | {p['gain']} | {p['loss']} | {p['both_retained']} | {p['both_lost']} | {p['compared']} |")
    j = report['journal']
    lines.extend(['', '## Attempts and faults', '',
        f"Physical native attempts: {j['attempts']['native']}; successful native calls: {j['successful_calls']['native']}. "
        f"Score attempts: {j['attempts']['scores']}; successful score calls: {j['successful_calls']['scores']}.", '',
        f"Fault records: {len(j['faults'])}; uncertain attempts: {len(j['uncertain_attempt_ids'])}; open session: {j['open_session']}.", '',
        f"Recorded closed-session seconds: {j['closed_session_seconds']:.6f}. "
        + ('This is a lower bound because a session remains open.' if j['open_session'] else 'All recorded sessions are closed.'), '',
        f"Budget flags: {', '.join(j['budget_flags']) or 'none in recorded accounting'}.", '',
        'Execution time is summed from physical successful calls once, including sentinel/timing calls. '
        'Cache reuse does not create another physical call. Failure duration may be absent.', '',
        '## Limits and remaining review', ''])
    lines.extend('- ' + text for text in report['limitations'])
    lines.extend(['', 'Week-6 acceptance remains pending. See analysis.json for exact source identities and missing keys.', ''])
    return '\n'.join(lines)


def write_output(path, files, protected):
    out = Path(path).resolve()
    for root in protected:
        root = Path(root).resolve()
        require(not out.is_relative_to(root) and not root.is_relative_to(out), 'Output overlaps protected inputs')
    require(not out.exists(), 'Output already exists; choose a new directory')
    out.mkdir(parents=True, exist_ok=False)
    for name, value in files.items():
        raw = (value.encode() if isinstance(value, str) else canonical(value) + b'\n')
        with (out / name).open('xb') as f:
            f.write(raw)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['readiness', 'filter'])
    for name in ('prepared', 'runner', 'package', 'protocol', 'out'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--review', type=Path)
    p.add_argument('--filter-run', type=Path)
    a = p.parse_args(argv)
    require(a.mode != 'readiness' or a.filter_run is None, 'Readiness mode cannot analyze a run')
    require(a.mode != 'filter' or (a.review is not None and a.filter_run is not None),
            'Filter mode requires --review and --filter-run')
    prepared = load_prepared(a.prepared, a.runner, a.package, a.protocol)
    protected = [a.prepared, a.runner, a.package, a.protocol, Path(__file__).resolve().parent]
    attribution = dict(preparation_sha256=prepared['digest'],
        analysis_code={f.name: sha(read(f)) for f in sorted(Path(__file__).parent.glob('*.py'))},
        challenge_review_sha256=None)
    review, contexts, review_problem = None, None, 'Independent challenge review not supplied'
    if a.review:
        protected.append(a.review)
        raw = read(a.review)
        review = decode(raw)
        attribution['challenge_review_sha256'] = sha(raw)
        try:
            contexts = reviewed_contexts(prepared, review)
            review_problem = None
        except (ValueError, KeyError, TypeError, StopIteration) as error:
            if a.mode == 'filter':
                raise ValueError('Challenge review invalid or pending: ' + str(error)) from error
            review_problem = str(error)
    if a.mode == 'readiness':
        report = dict(schema='filterflip-week06-readiness-v1', provenance=attribution,
            preparation_and_selected_source_checks='passed', saved_contexts=len(prepared['contexts']),
            challenge_anchors=len(prepared['draft']['anchors']),
            challenge_review_status='resolved_declaration' if contexts is not None else 'pending_or_invalid',
            challenge_review_issue=review_problem,
            expected_contexts_after_review=len(contexts) if contexts is not None else None,
            research_calls=0, models_loaded=0, experiment_status='not inspected or executed by readiness mode',
            milestone_acceptance='pending',
            note='A structurally resolved challenge review does not establish outcome verification, runtime readiness, or Week-6 completion.')
        text = '# Week-06 offline readiness check\n\n' + \
            'Preparation, selected source files, original runner code and protocol checksums match.\n\n' + \
            f"Saved contexts: 295. Draft challenge trios: 10. Review status: {report['challenge_review_status']}.\n\n" + \
            (('Review issue: ' + review_problem + '.\n\n') if review_problem else '') + \
            'No models loaded and no research calls made. This does not mark Week 6 complete.\n'
        write_output(a.out, {'readiness.json': report, 'README.md': text}, protected)
    else:
        protected.append(a.filter_run)
        require(not (a.filter_run / 'RUN.lock').exists(), 'Run lock exists; wait for a stopped run or investigate stale lock')
        log = journal(a.filter_run / 'journal.jsonl')
        identity = log['identity']
        require(identity['preparation_sha256'] == prepared['digest'] and
                identity['review_sha256'] == attribution['challenge_review_sha256'] and
                identity['code'] == prepared['manifest']['code'], 'Run identity mismatch')
        validate_rows(log, contexts, prepared['plan'])
        snapshot = a.filter_run / 'filter_results.json'
        if snapshot.exists():
            saved = decode(read(snapshot))
            require(saved['identity'] == identity and saved['complete'] is True and
                    len(log['rows']) == len(contexts), 'Invalid completed snapshot')
            require(saved['records'] == [log['rows'][c['key']] for c in contexts], 'Snapshot/journal mismatch')
        report = summarize(log, contexts)
        report['provenance'] = dict(attribution, filter_identity=identity, snapshot_present=snapshot.exists())
        # Detect ordinary concurrent writes between reading and exporting; stopped input is required.
        require(sha(read(a.filter_run / 'journal.jsonl')) == log['digest'] and
                not (a.filter_run / 'RUN.lock').exists(), 'Run changed during audit')
        write_output(a.out, {'analysis.json': report, 'REPORT.md': markdown(report),
            'support_review_TEMPLATE.json': review_template(report, log),
            'support_review_packet.txt': packet(log)}, protected)
    print('Offline audit saved to ' + str(a.out.resolve()) + '; no research calls made.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, StopIteration, RecursionError) as error:
        print('Audit stopped: ' + str(error), file=sys.stderr)
        sys.exit(2)
