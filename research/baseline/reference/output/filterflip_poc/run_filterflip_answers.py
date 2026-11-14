#!/usr/bin/env python3
"""Pair unfiltered/filtered answers for all nine frozen smoke cases (18 calls).
Uses saved native filter decisions; no filter reruns, retrieval or attack search.
"""
import argparse
import hashlib
import json
import time
import urllib.request
from pathlib import Path


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding='utf-8')


def api(endpoint, payload=None):
    req = urllib.request.Request('http://127.0.0.1:11434/api/' + endpoint,
        data=None if payload is None else json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=600 if endpoint == 'chat' else 30) as response:
        result = json.load(response)
    if result.get('error'):
        raise RuntimeError(result['error'])
    return result


def prepare(source, generator_run):
    plan = json.loads((source/'plan.json').read_text())
    prior = json.loads((generator_run/'experiment.json').read_text())
    rows = [json.loads(s) for s in (source/'results.jsonl').read_text().splitlines()]
    native = {r['case_id']: r for r in rows}
    if len(rows) != 9 or len(native) != 9 or len(plan['cases']) != 9:
        raise ValueError('Expected all nine completed smoke cases, without duplicates.')
    calls = []
    for case in plan['cases']:
        r = native[case['case_id']]
        docs = case['passages']
        ids = [d['id'] for d in docs]
        if r['status'] != 'ok' or r['input_ids'] != ids:
            raise ValueError('Saved filter result is incomplete or passage order changed.')
        for d in docs:
            if hashlib.sha256(d['text'].encode()).hexdigest() != d['sha256']:
                raise ValueError('Saved passage hash mismatch.')
        indices = r['removed_indices']
        if len(set(indices)) != len(indices) or any(type(i) is not int or i < 0 or i >= len(ids) for i in indices):
            raise ValueError('Invalid saved removal indices.')
        kept = [d for i, d in enumerate(docs) if i not in set(indices)]
        if [d['id'] for d in kept] != r['kept_ids']:
            raise ValueError('Saved removal indices and retained IDs disagree.')
        for mode, chosen in [('unfiltered', docs), ('filtered', kept)]:
            context = '\n\n'.join(d['text'] for d in chosen)
            if len(context) > 6000:
                raise ValueError('Unexpectedly large context; stop and inspect.')
            calls.append(dict(call_id=f"{case['case_id']}__{mode}", case_id=case['case_id'],
                condition=case['condition'], order=case['order'], mode=mode,
                passage_ids=[d['id'] for d in chosen],
                support_count=sum(d['supports_answer'] for d in chosen),
                expected_answer=plan['expected_answer'], context=context,
                context_sha256=hashlib.sha256(context.encode()).hexdigest(),
                request={'model': prior['model']['name'], 'stream': False,
                         'options': prior['options'], 'messages': [
                    {'role': 'system', 'content': prior['system_prompt']},
                    {'role': 'user', 'content': f"Document:\n<document>\n{context}\n</document>\n\nQuestion: {plan['query']}"}]}))
    return plan, prior, calls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path('results/filterflip_smoke_run1'))
    parser.add_argument('--generator-run', type=Path,
        default=Path.home()/'DocGuard-PoC/docguard_laptop_poc/results/llm_smoke_run1')
    parser.add_argument('--out', type=Path, default=Path('results/filterflip_answers_run1'))
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    plan, prior, calls = prepare(args.source, args.generator_run)
    if args.check_only:
        print('Input check passed: all 9 saved cases, 18 paired model calls. No model calls made.')
        print('The earlier model name, system prompt and generation settings will be reused.')
        return
    if args.out.exists():
        raise SystemExit('Output already exists; preserve it and use a fresh --out if needed.')
    version, tags = api('version'), api('tags')
    matches = [m for m in tags.get('models', []) if m.get('name') == prior['model']['name']]
    if version != prior['ollama'] or len(matches) != 1 or matches[0].get('digest') != prior['model']['digest']:
        raise SystemExit('Ollama version or model identity changed. Stop and inspect before comparing.')
    args.out.mkdir(parents=True)
    save(args.out/'experiment.json', dict(model=matches[0], ollama=version,
         options=prior['options'], system_prompt=prior['system_prompt'],
         source_plan=plan, calls=calls, source_filter_results=(args.source/'results.jsonl').read_text(),
         script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         scope='One fictional source in multiple conditions/orders, not 18 independent samples. No retrieval. No change to filter settings. All cases included, including clean-case failures.'))
    for call in calls:
        folder = args.out/call['call_id']
        folder.mkdir()
        save(folder/'request.json', call['request'])
        (folder/'context.txt').write_text(call['context'], encoding='utf-8')
    summary = ['FilterFlip paired answer test: one fictional source, all nine saved cases.',
               '18 calls; fixed contexts, no retrieval. Read full answers; support labels are authored fixture labels.', '']
    with (args.out/'results.jsonl').open('w', encoding='utf-8') as handle:
        for i, call in enumerate(calls, 1):
            row = {k: v for k,v in call.items() if k not in ('context', 'request')}
            print(f"[{i}/18] {call['call_id']} ...", flush=True)
            start = time.perf_counter()
            try:
                response = api('chat', call['request'])
                save(args.out/call['call_id']/'response.json', response)
                answer = response.get('message', {}).get('content')
                if response.get('done') is not True or not isinstance(answer, str):
                    raise ValueError('Incomplete or malformed model response.')
                row.update(answer=answer, done_reason=response.get('done_reason'),
                    status='truncated' if response.get('done_reason') == 'length' else 'ok' if answer.strip() else 'empty_response',
                    expected_literal_present=call['expected_answer'].casefold() in ' '.join(answer.split()).casefold())
            except Exception as error:
                row.update(status='fault', answer=None, error=f'{type(error).__name__}: {error}', expected_literal_present=None)
                save(args.out/call['call_id']/'error.json', row)
            row['wall_seconds_including_load'] = round(time.perf_counter()-start, 3)
            handle.write(json.dumps(row, ensure_ascii=False)+'\n')
            handle.flush()
            display = row.get('error') if row['status'] == 'fault' else row['answer']
            block = (f"{call['case_id']} | {call['mode']} | {row['status']}\n"
                     f"  Supporting passages: {call['support_count']}\n"
                     f"  Expected: {call['expected_answer']}\n  Answer: {display}\n")
            print(block, flush=True)
            summary.append(block)
            (args.out/'summary.txt').write_text('\n'.join(summary), encoding='utf-8')
            if row['status'] == 'fault':
                raise SystemExit('Stopped on model-call fault. Preserve this run and share the error.')
    print(f"Finished. Share {args.out/'summary.txt'}")


if __name__ == '__main__':
    main()
