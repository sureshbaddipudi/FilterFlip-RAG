#!/usr/bin/env python3
"""Render the Task-4 structured registers as portable Markdown; no application execution."""
from pathlib import Path
import json
import argparse


def build(p):
    read=lambda name:json.loads((p/(name+'.json')).read_text())
    write=lambda name,text:(p/name).write_text(text.strip()+'\n')
    controls,risks,evidence,rows,standards=(read(n) for n in ['CONTROL_REGISTER','RISK_REGISTER','EVIDENCE_REGISTER','RISK_MAPPING','STANDARD_REFERENCES'])
    anchors=read('CODE_ANCHORS')
    link=lambda file:'['+file+'](sources/'+file+')'
    ids=lambda values:', '.join(values)
    title='# FilterFlip-RAG — Task 4: consolidated security-risk mapping\n\n31 October 2026 · coursework checkpoint · prepared by the assistant for Suresh’s review\n\n'
    write('REPORT.md',title+'''
Task 4's mapping deliverable is complete: **46 taxonomy entries, 12 traced controls and 14 residual risks**. It covers six STRIDE threats and all ten entries in each approved OWASP Web, API, LLM and ML list. Inclusion means applicability was assessed; it does not mean 46 vulnerabilities were found, 46 tests passed, or any category was certified safe. Reviewer acceptance and any decision to accept residual risk are not recorded by this assistant-authored mapping.

The strongest research fit is **LLM08:2025 (Vector and Embedding Weaknesses)** and **ML01:2023 (Input Manipulation Attack)**. This is a project-specific interpretation: correct answer-bearing copies change retrieval/context composition and filtering, sometimes removing sufficient support. The main correct-copy experiment has no instruction override and does not demonstrate training-data or model-weight poisoning. Prompt-injection challenges, false-claim challenges and output-file tampering are separate scenarios.

## What the evidence establishes

The accepted primary result stays **8 events / 51 non-events / 0 unresolved classifications among 59 selected cases**. These are selected-case findings, with agreed post-outcome core-answer and mixed-answer rules; they are not a population attack-success rate. Eight cases have specific joint adjudication; the wider confirmation record does not turn every case into a blinded, unaided or jointly signed assessment.

Accepted Week-6 mitigation remains mixed: CN versus N has seven core-answer gains, eight losses and one uncertain comparison; two new false-claim harms and one avoided harm. **R110 remains uncertain.** New Task-2 comparisons and Task-3 answers await human review under Task 7. Task 3's 60 complete distinct responses / 72 logical positions establish execution and integrity, not semantic acceptance or full TrustRAG failure. Later TrustRAG stages were not evaluated.

The local application has request validation, fixed routes/process arguments, literal text rendering, release checks, private storage, bounded work, and partial/failure preservation. The mapping links these controls to named source symbols and existing test methods. Fresh offline Task-4 checks resolved **84 code/test references**, verified **53 unchanged source snapshots**, and checked **all 156 current v2.4 release entries**. They did not execute model inference, the application test suite, dependency scanners, or browser probes.

The recorded application logs contain 42 synthetic tests in normal and optimized Python; Task 3 has its own 19 synthetic checks in both modes. These retain their execution versions and scope. They are not added into a single security coverage score. Current source byte identity supports only the named unchanged surfaces. The earlier browser fixture does not validate every later JavaScript change.

## Where protection remains limited

- Local checksums and chained logs establish consistency, not authentic origin, external nonrepudiation, reviewer identity or absence of backdoors in approved assets.
- The browser request token is protection against cross-site requests, not user authentication. It does not guard the separate local Ollama API. The trusted operating-system account remains an assumption.
- Finite job/time/output limits reduce operational exposure. They do not impose hard RAM or filesystem quotas and do not prevent the research mechanism of losing answer support.
- Literal rendering and fixed subprocess arguments address application injection sinks. They do not prove resistance to instructions embedded in model context.
- The preserved 71 dependency component/advisory records require relevance assessment. They are not 71 demonstrated exploits or a fresh scan. Private training-data privacy, public hosting, model tools/actions, training and parameter updates were not evaluated.

## Editions and authority

'''+'\n'.join('- ['+s['id']+' — '+s['edition']+']('+s['url']+'): '+s['status']+'.' for s in standards)+'''

Official pages were checked on 31 October 2026. The [OWASP ML project](https://owasp.org/projects/machine-learning-security-top-ten) explicitly describes the work as a draft. This mapping pins the ML:2023 identifiers rather than claiming a finalized certification standard. ML06 has an index/page title variation, preserved in its row. No OWASP or Microsoft endorsement of the project mapping is implied.

Latest explicit user instructions and the [current handover](sources/current_handover.md) govern scope. Attributed acceptance overlays govern scientific decisions; earlier report bytes and missing dates are preserved. The old Week-4 backlog and later demo reuse SEC identifiers for different meanings: see the qualified [crosswalk](LEGACY_ID_CROSSWALK.md). CTRL01–CTRL12 are navigation identifiers, not silent renames of old requirements.

## Read and reproduce this checkpoint

1. Read the [trust boundaries](THREAT_MODEL.md) and [execution profiles](EXECUTION_PROFILES.md).
2. Use the [46-entry mapping](RISK_MAPPING.md), [control traceability](CONTROL_TRACEABILITY.md) and [evidence register](EVIDENCE_REGISTER.md) to inspect the basis and limit of each claim.
3. Review the [14 residual risks and later-task handoff](RESIDUAL_RISKS_AND_FOLLOWUP.md). Use the [review guide](REVIEW_GUIDE.md) for acceptance; no new review has been attributed to Suresh or Shradha here.
4. Follow [README.md](README.md) to run the portable offline validator. [The saved check](validation/MAPPING_CHECK.json) records the authoring-machine integrity comparison.

Task 5 is next in the approved sequence: assess dependency relevance and selected fixes in a separate environment. Task 6 reconciles teammate testing evidence and release binding; Task 7 reviews new outcomes; Task 9 verifies selected security changes and scientific compatibility. Larger datasets and a new mitigation research programme remain deferred. Task 4 changes no application code, model, scientific input, accepted label, original review or Desktop file.
''')
    write('THREAT_MODEL.md','''
# Task 4 — trust boundaries and threat model

31 October 2026. Scope: local, single-user coursework demonstration plus separately bounded research runners. This is a model of the supplied system, not a public-service deployment approval.

```mermaid
flowchart LR
  B["Browser requests"] -->|"Host / Origin / token / schema"| A["Local application API"]
  A -->|"Fixed arguments / one owned job"| W["Owned worker"]
  S["Untrusted corpus and copied passages"] -->|"Verified fixture identity"| W
  T["Trusted local code, config and model identities"] --> W
  W --> R["Retrieval and filtering"]
  R -->|"Evidence-only prompt / bounded request"| M["Dedicated local model service"]
  M -->|"Untrusted response / shape and stop checks"| W
  W -->|"Raw responses / partial states"| F["Private run files and event records"]
  F --> A
  A -->|"Literal text display / export"| B
  L["Trusted local account or process"] -.->|"Separate model API; app token does not apply"| M
  H["Human review and attributed overlays"] --> F
```

The graph shows logical boundaries. Browser and model ports differ; a loopback address is a location constraint, not an identity for every local process. Task 3's command-line worker bypasses the browser API and has its own controls/profile. It does not acquire all GUI quotas merely by using the same model port.

## Assets and actors

| Asset | Why it matters | Principal threat |
|---|---|---|
| Sufficient answer support and usable answers | Core research objective | Valid correct-copy input can cause support loss; wrong claims can survive |
| Frozen methods, encoder/model identities and request settings | Comparable results | Replacement, drift, malicious approved artifact or mistaken configuration |
| Raw replies, run states, review attribution and accepted overlays | Reconstructable science | Fabricated completion, silent retry, mutable provenance or overclaimed review |
| CPU, memory, disk and service availability | Finish a bounded demonstration | Excess jobs, slow responses, large output or incomplete cleanup |
| Local files, passages, review details and paths | Intended evidence access | Unintended disclosure or unrestricted export |

The main research adversary can insert one or two copies of an accessible source for a known target question. Original records, the question, embeddings/settings and compared defenses are held fixed. Corpus insertion is simulated; ingestion compromise is not demonstrated. Background-source copies are controls. Adding a false claim or an instruction is a separate challenge. Evaluator-only correct-source labels must not become a defense shortcut.

An application adversary may send malformed or cross-origin browser requests, supply dangerous-looking corpus/model text, consume resources, or manipulate local artifacts if a trust assumption fails. The system assumes a trusted operating-system account, configuration, interpreter, pinned inputs and installed model assets. Compromise of that account or dependency can defeat local checks; hashes do not eliminate this scenario.

## Boundary-to-control trace

| Boundary | Data or authority crossing | Controls | Remaining limit |
|---|---|---|---|
| Browser → local app | Select case/mode/condition, read saved runs, request cancellation | CTRL01, CTRL02, CTRL04, CTRL06 | No user roles/authenticated reviewers; trusted local process can obtain/use token |
| App → worker and files | Fixed command, output folder and settings | CTRL03, CTRL04, CTRL05, CTRL08 | Trusted local code/config/account; no general OS sandbox |
| Corpus → retrieval/filter/model | Untrusted text and input composition | CTRL03, CTRL10, CTRL11 | Valid inputs still cause observed support loss; no general mitigation |
| Worker → separate model API | Fixed loopback calls and frozen generation | CTRL03, CTRL05, CTRL06, CTRL11, CTRL12 | App nonce does not protect direct API access or audit all service-management routes |
| Model/file → GUI/export/reviewer | Untrusted text and partial raw output | CTRL04, CTRL05, CTRL09, CTRL10, CTRL11 | Intended exports expose full evidence; no external authenticity/privacy guarantee |
| Dependencies/checkpoints → execution | Executable/native code and learned parameters | CTRL03, CTRL12 | Open advisories, origin/backdoor uncertainty and check-to-use limitations |

STRIDE denial of service is recorded in two senses: operational resource exhaustion and the research loss of a supported answer. A request quota controls the former; it does not repair the latter. Similarly, an unchanged raw answer may be wrong, and a correct answer may be unsupported by supplied evidence. Byte integrity, semantic correctness and scientific review are separate checks.

No public hosting, multi-user roles, confidential training cohort, training/fine-tuning/feedback updates, private model-IP objective, uploads, SQL sink or model-controlled tool/action executor is included. The [mapping](RISK_MAPPING.md) records the relevant exclusions and triggers for reassessment rather than marking those categories passed.
''')
    write('EXECUTION_PROFILES.md','''
# Task 4 — deployment and execution profiles

These profiles are separate. The figures below describe named code or saved audits, not measured robustness under every workload.

| Profile | Entry point and work | Bounds / evidence | Limit of inference |
|---|---|---|---|
| GUI v2.4 | Loopback browser API, default port 8767; fixed owned worker and dedicated model API | One job; eight HTTP slots; 1,024-byte JSON body; 8,192 parsed header characters; 3-second socket timeout; four answer attempts; 128 output tokens; 590 seconds/request; 2,400 seconds/job | Parsed header check is not a complete pre-parse network-byte quota; no hard RAM quota or public load assurance |
| GUI storage | Private local run folders and selected exports | 2 MiB model response; 128 MiB/run; admission at fewer than 60 runs and less than 1 GiB archive; at least 1 GiB free to start; stop below 256 MiB free | Poll/admission checks can overshoot; no filesystem quota; storage modes do not encrypt evidence |
| Task 1 recovery | Separate audited continuation/recovery worker; dedicated port 11436 | 706 unique requests accounted: 705 complete and one retained truncation; original ambiguous 286/487 records preserved plus explicitly authorized retries | 581 continuation/recovery starts; 709 physical starts including original 128. Amended time accounting is not proof actual historical active total stayed within eight hours |
| Task 2 | Offline secondary-variant analysis of existing data | All 59 cases and all nine original variants; no model or HTTP call | Computational comparisons are not new semantic event labels |
| Task 3 | Separate stage-1 survivors + evidence-only Qwen command-line run | 60 study requests + one synthetic setup start; 72 logical positions; 7,200-second active cap; 600-second request / 60-second metadata limits; 128 output tokens; 2 MiB raw response | Saved run used 1,728.809711793 active seconds and 61 starts; no retries/truncations. Human semantic review pending. Does not inherit GUI archive/disk quotas |
| Task 4 | Offline source/register inspection and validator | 53 snapshot hashes, 84 symbol references, 156 current application release entries | No models, security scanner or fresh app/browser test execution |

The GUI model service and Task 3 both use 11437 in their respective configurations. They require exclusive, nonconcurrent ownership; that shared number is not simultaneous isolation. Task 3 refuses an already occupied endpoint. Ordinary system Ollama at 11434 is separate. Ownership must be established afresh before starting/stopping any service; historic PIDs are not authorization.

## Browser-facing route inventory

| Method | Route | Function / restriction |
|---|---|---|
| GET | `/`, `/app.js`, `/style.css` | Three fixed application assets |
| GET | `/api/bootstrap` | Cases, active run and browser mutation token; token is not login |
| GET | `/api/reference/<case>` | Exact known case lookup, no arbitrary file path |
| GET | `/api/runs/<32-hex-id>` | Validated existing private run snapshot; run ID is not cross-user authorization |
| HEAD | Same GET handlers | Headers without response body |
| POST | `/api/runs` | Exact allowed selection fields, known case/mode/condition, one-job/storage checks |
| POST | `/api/cancel` | Exact `run_id` property and matching active run |
| Other | Explicit PUT/PATCH/DELETE/OPTIONS/TRACE/CONNECT handlers | Rejected; unsupported methods follow base-handler behavior |

All GET/POST handlers apply their relevant local-origin/framing checks. Route inventory source: `Handler.do_GET`, `Handler.do_POST`, `Handler.do_HEAD` in [server.py](sources/app/server.py). The bootstrap token and Host/Origin checks protect the browser boundary under the single-account assumption; they are not per-user object ownership.

## Separate model-client interface

The inspected UI client uses fixed local model-service version, tags, show and chat calls. Task 3 also uses ps to check CPU placement. These are the calls used by this project, **not an exhaustive inventory or security review of Ollama's separate management API**. Browser input cannot choose an arbitrary destination; clients reject proxies/redirects. Trusted local configuration and installed executables remain separate assumptions.

The UI preserves raw output and stops on truncation. The explicitly approved Task-1/Task-3 protocols may preserve a truncation and continue other distinct requests under their own rules. No profile permits silently retrying an ambiguous call. A complete process/run state is not human acceptance of an answer.
''')
    out=['# Task 4 — control traceability','', 'Controls are traced to snapshots and existing tests. Test names identify specific checks, not whole-category certification. Recorded logs and version binding are in the evidence register. No fresh app or Task-3 test execution occurred in Task 4.','']
    for c in controls:
        out += ['## '+c['id']+' — '+c['requirement'],'', 'Historical demo identifier: `'+c['legacy_namespace']+'`. Status: '+c['status'].replace('_',' ')+'.','',c['implementation'],'','Code references:','']
        for r in c['code']:
            out += ['- '+link(r['file'])+' — `'+r['symbol']+'`, line '+str(anchors[r['file']][r['symbol']])+'.']
        if c['id']=='CTRL05':out += ['- '+link('app/static/app.js')+' — `el` at line 6 uses `textContent`; inspected current source, not a fresh browser fixture.']
        out += ['','Existing test references:','']
        for r in c['test_references']:out += ['- '+link(r['file'])+' — `'+r['symbol']+'`, line '+str(anchors[r['file']][r['symbol']])+'.']
        out += ['','Evidence: '+ids(c['evidence_ids'])+'.','', '**Limit:** '+c['residual_limit'],'']
    out += ['## Release binding','',read('BASELINE_CODE_BINDING')['scope'],'','See [BASELINE_CODE_BINDING.json](BASELINE_CODE_BINDING.json). Guard/backend/policy/test byte identity to the named historical versions does not extend to every changed display path or establish the version used for teammate live runs.']
    write('CONTROL_TRACEABILITY.md','\n'.join(out))
    out=['# Task 4 — complete applicability matrix','', '46 rows; six STRIDE and ten per OWASP list. This is the project-specific mapping of the supplied system. Each entry connects a scenario to controls, evidence, residual risk and scope. An excluded feature is not a safety pass. All entries have status `applicability_mapped_not_category_certified`.','', 'Use [control traceability](CONTROL_TRACEABILITY.md) for exact code and test methods, [evidence](EVIDENCE_REGISTER.md) for execution attribution, and [residual risks](RESIDUAL_RISKS_AND_FOLLOWUP.md) for later tasks. IDs are edition-qualified. ML:2023 remains a draft.','']
    for standard in standards:
        out += ['## '+standard['id']+' — '+standard['edition'],'','[Official source]('+standard['url']+'). '+standard['status']+'.','']
        for r in [x for x in rows if x['framework']==standard['id']]:
            out += ['### '+r['id']+' — '+r['title'],'','Applicability: **'+r['applicability'].replace('_',' ')+'**.','',r['scenario'],'','| Trace | Reference |','|---|---|','| Controls / related tests | '+ids(r['controls'])+' |','| Residual risks | '+ids(r['risk_ids'])+' |','| Attributed evidence | '+ids(r['evidence_ids'])+' |','', '**Remaining gap:** '+r['remaining_gap'],'','**Scope / reassessment:** '+r['scoped_exclusion_or_reassessment_trigger'],'','[Official taxonomy reference]('+r['official_reference']+').','']
    write('RISK_MAPPING.md','\n'.join(out))
    out=['# Task 4 — attributed evidence register','', 'Read/hash/trace evidence is not a new execution. Source snapshot hashes and original paths are in [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json). Attribution and unknowns remain as recorded. The sources are copies; no old review or raw evidence was edited.','']
    for e in evidence:
        out += ['## '+e['id']+' — '+e['title'],'',link(e['file']), '', e['attribution_and_scope']+'.', '', 'Task-4 action: '+e['task04_action']+'.','']
    out += ['## Fresh Task-4 work','', 'The offline [validation record](validation/MAPPING_CHECK.json) checks source hashes, structured references, categories and recorded log summaries. It also compares all 156 entries of the original current release manifest on the authoring machine. This is an integrity/traceability check, not an application penetration test, scanner run, model execution or human scientific acceptance.','', 'The 53 selected snapshots are supporting context, not a complete runnable model/reproduction archive. Existing packages stay authoritative for their full raw data. No model weights, local configuration, credentials or Desktop deployment were copied into this packet.']
    write('EVIDENCE_REGISTER.md','\n'.join(out))
    out=['# Task 4 — residual risks and follow-up','', 'All 14 risks remain open or partially controlled. This assistant-authored mapping records no risk acceptance, formal severity score or measured likelihood. Priority labels guide the already approved coursework sequence; they do not manufacture CVSS values.','']
    for r in risks:
        out += ['## '+r['id']+' — '+r['title'],'',r['scenario'],'','Controls: '+ids(r['controls'])+'. Evidence: '+ids(r['evidence_ids'])+'.','', '**Residual:** '+r['residual_gap'],'', '**Follow-up:** approved task(s) '+', '.join(map(str,r['follow_up_tasks']))+'. Priority basis: '+r['priority'].replace('_',' ')+'; '+r['priority_basis']+'.','', 'Risk acceptance: '+r['risk_acceptance']+'.','']
    out += ['## Concrete handoff within the approved plan','', '| Task | Needed result | Current boundary |','|---|---|---|','| 5 — dependencies / selected fixes | Reconcile exact component versions/advisory aliases/platform constraints; assess reachability; choose justified fixes in a separate environment | Preserved 71 component/advisory records are version-match evidence. Do not silently patch accepted baseline or assume a listed fix preserves scientific outputs |','| 6 — testing reconciliation | Obtain raw commands, environment/source identity, logs, coverage/scanner units, probe results and an attributed addendum through Suresh | The testing PDF reports 42 tests, 55% overall coverage and additional checks; missing raw support stays missing |','| 6 — live-log reconciliation | Bind exact UI/static release; reconcile report 0/15 with supplied exposure/answer counts; record reasons/corrections for four pre-generation integrity failures if supplied | 27 attempts, 22 completed / 88 answers; backend byte identity does not prove UI version |','| 7 — outcome review | Review new reproduction, secondary and stage-1 answers; compare exact support, core completeness and wrong extras; resolve material disagreements jointly | Earlier exact four-run acceptance and all original attributions remain. Additional 19 completed runs / 76 answers are not automatically accepted |','| 8 — paired analysis | Integrate reviewed differences, negative results and insertion-versus-retrieval qualifications | No new event labels from lexical matches or execution success alone |','| 9 — selected security verification | Target the changed control and scientific compatibility in an isolated environment; document changed outputs and unresolved risks | No full research regeneration by default; no blanket closure from synthetic guards |','| 11 / 13 — final report and handover | Carry version/edition limits, uncertainty and scoped exclusions into final deliverables | Risk acceptance and reviewer decisions require an attributed record |','', 'The supplied logs have four instruction runs / 16 outputs, ten marker-exposed outputs and zero literal marker matches. These counts do not establish the testing report’s 0/15 denominator. The accepted research result of nine instruction cases per policy with no observed marker successes remains a different, narrowly scoped result.','', 'The four failed attempts report an index.html integrity mismatch before generation. Their intended cause/correction is unknown; do not label them deliberate successful tampering tests. Completed Heather neutral and false-claim runs exist. Historical GUI text that says these variants remain outside live validation needs reconciliation, rather than erasing the later intake or declaring every later answer accepted.','', 'Training, parameter poisoning, privacy attacks, private model theft, public multi-user hosting and agent tools/actions are scoped out or conditional as specified in the category rows. Reassess if the corresponding feature/asset is introduced. Larger-dataset expansion and a new mitigation programme are deferred until after coursework; this list does not authorize them.']
    write('RESIDUAL_RISKS_AND_FOLLOWUP.md','\n'.join(out))
    out=['# Task 4 — historical security identifier crosswalk','', 'Week-4 backlog SEC identifiers and later demo SEC identifiers refer to different lists. This packet uses CTRL01–CTRL12 and qualifies historical IDs with a namespace. Links indicate related scope, not one-to-one renaming, automatic old-backlog completion or a new acceptance decision.','', '| Historical backlog ID | Current related controls |','|---|---|']
    for r in read('LEGACY_ID_CROSSWALK'):out += ['| '+r['historical_id']+' | '+ids(r['current_control_ids'])+' |']
    out += ['', 'Later demo IDs appear as `DEMO-v2:SEC-01` through `DEMO-v2:SEC-12` in [CONTROL_REGISTER.json](CONTROL_REGISTER.json). Read the unchanged [Week-4 backlog](sources/week04_backlog.md) and [demo security record](sources/app/SECURITY.md) for their original wording and status.']
    write('LEGACY_ID_CROSSWALK.md','\n'.join(out))
    write('REVIEW_GUIDE.md','''
# Task 4 — review guide for Suresh and Shradha

This packet is prepared for review. No new decision is attributed to either reviewer, and no message has been sent to Shradha. Suresh can forward the ZIP when appropriate. No new upload or re-extraction of the original reproduction package is needed.

1. Read REPORT.md, THREAT_MODEL.md and EXECUTION_PROFILES.md. Check whether each claimed boundary matches the intended local demonstration.
2. Review RISK_MAPPING.md. For each disputed row, record category ID/edition, the exact disputed scenario or exclusion, source/evidence ID and proposed correction. Distinguish correct-copy input manipulation from instruction injection, training poisoning and output tampering.
3. Follow controls to named code and existing tests in CONTROL_TRACEABILITY.md. Distinguish implementation, prior recorded execution, fresh integrity checking and pending independent verification.
4. Review RESIDUAL_RISKS_AND_FOLLOWUP.md. Agree what belongs to Task 5/6/7/9 and retain unresolved gaps. Mapping completeness does not require accepting the residual risks or inventing security passes.
5. Record the reviewer, actual date if known, reviewed package manifest hash, decision, scope, disagreements and remaining uncertainty. A recording date must not substitute for an unknown review date. No signature or blinded review should be inferred from this checklist.

Suggested return: an attributed Markdown addendum that names the reviewed package/manifest and lists accepted mapping rows, corrections and unresolved rows. Keep individual and joint decisions distinguishable. Task 7 separately accepts or disputes the new scientific outcomes. Do not alter frozen raw records or force R110 to a label.

Task 6's missing raw testing evidence and exact UI release binding are already documented. Request them through Suresh when doing that task; the existence of this guide does not claim they were received. Current official taxonomy links are edition-pinned in STANDARD_REFERENCES.json, with the ML draft limitation preserved.
''')
    write('README.md','''
# FilterFlip-RAG Task 4 — code and guide checkpoint

Start with [REPORT.md](REPORT.md). The mapping is complete as an artifact; human acceptance/risk acceptance is not recorded. This is a standalone mapping/inspection packet, not a runnable application, model bundle or replacement for the original evidence archive.

## Contents

- Human-readable mapping, threat diagram, execution profiles, control/test trace, evidence register, legacy-ID crosswalk, residual risks and review guide.
- Matching JSON registers for category/control/evidence/risk relationships.
- 53 unchanged selected source snapshots with SHA-256 bindings and exact code/test catalogs.
- Saved offline validation and an independently runnable standard-library validator. It does not import or execute the application, model libraries or supplied source snapshots.
- SHA256_MANIFEST.json binding every other file in the sealed packet. The sibling ZIP checksum binds the complete distribution; neither checksum is a digital signature.

## Offline check after extracting

From the extracted packet directory:

```bash
python3 -B code/validate_mapping.py --check-package
```

This prints PASS/FAIL and makes no file changes. It requires ordinary Python 3 and no model, external package, network connection, original absolute path or Desktop access. It checks the exact category sets/editions, foreign keys, code/test symbol locations, source snapshots, recorded log summaries, uncertainty fields and sealed inventory. It does not rerun the 42 app tests or 19 Task-3 tests.

Authoring-machine optional checks are `--check-originals --check-release`; these read the original paths listed in SOURCE_MANIFEST.json and all 156 current app release entries. The saved validation/MAPPING_CHECK.json includes those checks. Do not use these flags on another machine unless those exact source paths exist. Do not use `--write` on a sealed review copy: it is an authoring option and changes the package hash.

`code/build_reports.py` regenerates readable Markdown from the JSON registers and static narrative. It writes only inside the packet and should be used in a new versioned working copy, followed by review/revalidation/resealing. JSON changes require corresponding source/trace review; regenerating a report does not validate a changed scientific claim. `code/validate_mapping.py` independently parses source snapshots for its symbol checks. No original-source capture or model execution is hidden in either helper.

## Scope and preservation

Task 4 reads code and attributed records and writes this new mapping packet. Application code and release files, model settings, scientific inputs, accepted labels, original reviews, frozen evidence and Desktop files remain unchanged. No new model, scanner, application test or browser run is included. Saved prior logs retain attribution and version limitations. Official references are edition-pinned and checked on 31 October 2026; online pages may later change.

The next task is dependency relevance assessment and selected fixes (Task 5), in a separate environment. New scientific review and any selected-change verification remain Tasks 7 and 9. This package does not authorize larger datasets, a new mitigation programme, public deployment, or training/agentic features.
''')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent.parent)
    build(parser.parse_args().root)
