"""Track this one running experiment and audit its completed output; no model calls."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results/answers_run1'


def read_complete_rows(path):
    # The generator may currently be appending its next record.
    text = path.read_text()
    return [json.loads(line) for line in text.splitlines(keepends=True)
            if line.endswith('\n') and line.strip()]


def write_atomic(path, text):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(text)
    temp.replace(path)


def snapshot():
    calls = read_complete_rows(HERE / 'calls.jsonl')
    records = read_complete_rows(OUT / 'unique_results.jsonl')
    unique = {r['request_sha256']: r for r in records}
    assert len(unique) == len(records), 'Duplicate saved request hashes require review'
    assert set(unique) <= {c['request_sha256'] for c in calls}
    complete = [c for c in calls if unique.get(c['request_sha256'], {}).get('status') == 'ok']
    primary = Counter(c['case_id'] for c in complete if c['condition'] in ['C', 'BN1', 'PN1'])
    bad = [r for r in records if r['status'] != 'ok']
    age = time.time() - (OUT / 'unique_results.jsonl').stat().st_mtime
    status = ('requires_review' if bad else 'generation_complete_pending_audit'
              if (OUT / 'RESULT_MANIFEST.json').exists() else
              'no_recent_output_check_runner' if age > 1200 else 'in_progress')
    validation = HERE / 'VALIDATION.json'
    if status == 'generation_complete_pending_audit' and validation.exists():
        if json.loads(validation.read_text()).get('status') == 'passed':
            status = 'generation_complete_execution_audit_passed'
    info = dict(updated_utc=datetime.now(timezone.utc).isoformat(), status=status,
                saved_unique_responses=len(records), planned_unique_requests=706,
                completed_logical_conditions=len(complete), planned_logical_conditions=1062,
                fully_completed_primary_questions=sum(v == 6 for v in primary.values()),
                planned_questions=59, response_status_counts=dict(Counter(r['status'] for r in records)),
                last_response=records[-1]['first_call_id'] if records else None,
                seconds_since_last_response=round(age),
                note='Completion is not correctness. Semantic/outcome review and human verification remain separate.')
    write_atomic(HERE / 'PROGRESS.json', json.dumps(info, indent=2) + '\n')
    lines = ['# FilterFlip answer-run progress', '', 'Updated (UTC): ' + info['updated_utc'], '',
             '**Status:** ' + status.replace('_', ' '), '',
             f"Saved distinct responses: **{len(records)}/706**.",
             f"Completed logical answer conditions: **{len(complete)}/1062**.",
             f"Questions with all primary/control answers: **{info['fully_completed_primary_questions']}/59**.",
             '', info['note'], '', 'Last saved response: ' + str(info['last_response']), '',
             'The pending interrupted attempt was preserved before resuming; see results/answers_run1/recovery/.',
             'This report tracks a single already-running experiment. It never sends model requests or retries them.']
    write_atomic(HERE / 'PROGRESS.md', '\n'.join(lines) + '\n')
    finished = status == 'generation_complete_execution_audit_passed'
    refresh = '' if finished else '<meta http-equiv="refresh" content="30">'
    review_link = ('<a href="COMPLETED_RUN_REVIEW.md">Completed-run findings</a>'
                   if (HERE / 'COMPLETED_RUN_REVIEW.md').exists() else
                   '<a href="EARLY_OUTCOME_REVIEW.md">First reviewed examples</a>')
    footer = ('Generation is complete; this page no longer refreshes. Outcome review remains separate.' if finished else
              'This page refreshes every 30 seconds. Check the update time: a stale time means the tracker may have stopped.')
    body = ('<!doctype html><html lang="en"><meta charset="utf-8">' + refresh +
            '<title>FilterFlip progress</title>'
            '<style>body{font:18px system-ui;max-width:850px;margin:50px auto;padding:24px;'
            'line-height:1.6;background:#f7fafc;color:#172334}pre{white-space:pre-wrap}</style>'
            '<h1>FilterFlip answer-run progress</h1><pre>' + html.escape('\n'.join(lines[2:]).replace('**', '')) +
            '</pre><p>' + review_link + ' · '
            '<a href="PRIMARY_ANSWER_REVIEW.md">Paired answers</a></p>'
            '<p>' + footer + '</p></html>')
    write_atomic(HERE / 'PROGRESS.html', body)
    return info


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    deadline = time.monotonic() + 12 * 3600
    last_count = -1
    while True:
        info = snapshot()
        if info['saved_unique_responses'] != last_count:
            print(json.dumps(info), flush=True)
            last_count = info['saved_unique_responses']
        if info['status'] == 'generation_complete_pending_audit':
            for script in ['audit_answers.py', 'build_review.py']:
                subprocess.run([sys.executable, str(HERE / script)], check=True)
            snapshot()
            return
        if args.once or info['status'] in ['requires_review', 'generation_complete_execution_audit_passed']:
            return
        if time.monotonic() >= deadline:
            print('Tracker time limit reached. No experiment data or process was altered.', flush=True)
            return
        time.sleep(30)


if __name__ == '__main__':
    main()
