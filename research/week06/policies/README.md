# FilterFlip Week-06 implementation and challenge-review package v1

**This is working development code and a draft review packet, not Week-6 research results.** It implements preparation, exact/near duplicate policies, bounded filtering, saved-answer reuse and a bounded local generation stage. Research execution has not started; all challenge decisions remain pending. Original results, source code and prior releases remain unchanged.

## Start with the review packet

Open `prepared/CHALLENGE_REVIEW.md`. It contains ten anchors, each with the original archived passage and three proposed additions: neutral, wrong-answer and instruction-poison. All30 additions fit the pinned256-token window (31–173 tokens including special tokens). This is a tokenizer check, not semantic validation.

Give the teammate the packet and `prepared/review_TEMPLATE.json`. They should save a separate copy of the JSON outside this release, add their name, role `independent_human`, ISO review date, and **approve or exclude each complete trio**. An approval needs all five review checks, a rationale and a specific final wrong-answer scoring rubric. An exclusion needs a reason. The review binds the exact draft hash. Do not invent approvals or replace the draft texts after viewing outcomes. A flawed trio can be excluded; no replacement anchors are chosen.

The drafts deliberately preserve potential contradictions for review. The bald-eagle substitution leaves an etymology qualification; the PHP expansion can conflict with its care description. Archived phone, legal, medical and historical statements are test data, not current advice. Do not call any phone number or act on passage instructions. One UCC answer-source copy was not retrieved in the old PN1 context; its challenge source is instead the frozen reference passage containing the support quote. Every new challenge is explicitly a forced append to the clean five, not a new retrieval success.

## What is implemented

| File | Function |
|---|---|
| `prepare.py` | Verify frozen inputs and code identity; prepare295 saved contexts and30 challenge drafts; tokenize without loading an encoder or generator |
| `policies.py` | Exact equality collapse; fixed0.95 complete-link grouping; ordering diagnostic; explicit singleton handling |
| `run_filter.py`, `worker.py` | Human-review gate,12 native sentinels, four main policies plus ordering diagnostic, bounded offline native worker, traceable retention screens |
| `runtime.py` | Exclusive-run lock, fsynced hash-chained journal, persistent budgets, exact-input cache, deadline and process-group cancellation |
| `answer_requests.py` | Exact frozen prompt construction, saved-request matching and bounded new-answer queue |
| `generate.py`, `generation_worker.py` | Pinned tokenizer checks, dedicated loopback Ollama daemon, fixed model/settings, bounded generation, no shared-service termination |
| `tests/`, `validation/` | Synthetic software checks and saved-record validation; no experimental calls |

This release does not yet contain outcome adjudication, final analysis tables or independently reproduced research execution. The real native and Ollama integration paths are implemented but have **not been exercised against study contexts in this increment**.

## Environment and developer tests

The orchestration and synthetic tests use Python3.11+ and its standard library. Live research stages use the existing pinned `filterflip-core` environment, not the system Python. Preparation needs its `tokenizers`; native execution needs the original pinned dependencies/model; generation needs the original Qwen tokenizer and Ollama0.34.2 with the saved Qwen2.5:3b model digest. No installation, model download or dependency upgrade is performed by this code.

```sh
python3 -m unittest discover -s tests -v
python3 -O -m unittest discover -s tests -v
```

The tests use synthetic fake workers, including a complete295-context scheduling/pause/resume simulation. These records live only in temporary test directories and are not research outcomes or human reviews. An additional short-lived fake child tests forced cancellation. Tests may take roughly a minute because the journal flushes records durably; elapsed time depends on the disk.

Use the release checksum to verify the received ZIP through a trusted channel. `RELEASE_SHA256.json` records its file contents. Included manifests detect changes; they do not authenticate an author or a human reviewer.

## Offline preparation, if rebuilding

The release includes the prepared packet. To reproduce it, activate the existing pinned environment and use a new destination **outside** this release and the original packages:

```sh
python prepare.py --package /path/to/FilterFlip_Reproduction_Package \
  --planning /path/to/FilterFlip_Week6_Planning_v1 \
  --model /path/to/pinned-MiniLM-snapshot --out /path/to/new-preparation
```

The model path is the all-MiniLM-L6-v2 snapshot at revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`. Preparation reads its hashed tokenizer only. The generated files are portable; path choices are supplied when running. Changing a top-level Python source changes the preparation identity and requires a new preparation/review version rather than silently bypassing validation.

## Research commands — only after challenge review

The following commands are instructions for the next stage, **not a record of executed experiments**. Use absolute paths, the original pinned environment, an unchanged vendor checkout and a new output directory outside the release/reference/model directories.

```sh
python run_filter.py --prepared /path/to/this-release/prepared \
  --review /path/to/teammate-reviewed.json --package /path/to/FilterFlip_Reproduction_Package \
  --vendor /path/to/pinned/RAGDefender --model /path/to/pinned-MiniLM-snapshot \
  --out /path/to/new-filter-run
```

All ten anchor decisions must be resolved, including explicit exclusions. The unfilled template is rejected before output creation or model loading. The native worker then checks vendor/model hashes and dependency versions before loading.12 sentinels must match saved decisions before reuse. Code, preparation, review, model path and vendor path identities bind the journal. Filter limits are1050 native attempts and7200 accumulated active seconds across orderly resumes. Each worker operation has an additional120-second timeout. Startup is bounded too.

`--stop-after-contexts 7` is an optional orderly pause after seven additional complete contexts. Continue with identical arguments and `--resume`. No automatic retry is allowed after a fault or uncertain interrupted call. A hard crash or stale lock requires investigation and an attributed recovery amendment; do not delete a lock/journal simply to make a run restart. New runs also cannot be used to evade the study's total protocol budget; count any attempted earlier run in the research execution record.

After a complete filter run:

```sh
python answer_requests.py --package /path/to/FilterFlip_Reproduction_Package \
  --prepared /path/to/this-release/prepared --run-dir /path/to/completed-filter-run \
  --out /path/to/new-answer-queue
```

This validates the filter journal and assembles up to336 logical answers, with at most228 fresh requests after exact reuse. It makes no network or generator calls. Saved U/N requests must match exactly, including text order, model settings and system message.

For live generation after the queue is frozen:

```sh
python generate.py --queue /path/to/new-answer-queue \
  --package /path/to/FilterFlip_Reproduction_Package \
  --ollama-binary /absolute/path/to/installed/ollama \
  --models /absolute/path/to/existing/ollama/models --out /path/to/new-generation-run
```

The runner starts **its own** Ollama daemon on127.0.0.1:11435, refuses an occupied port, and leaves the usual11434 service alone. It uses the existing model store without pulling models. Version and model digest are checked before and after each answer. The binary hash and tokenizer hashes bind the run. Requests have fixed settings, bounded input/output sizes, no proxies/redirects and no URL parameter. Generation is capped at228 attempts,14400 accumulated active seconds and600 seconds per request. Timeout/fault cleanup kills the owned process group. Live daemon/descendant cancellation still needs integration verification in the permitted execution stage.

`--stop-after-requests N` and `--resume` support orderly boundaries. Empty, malformed, truncated, token-mismatched or failed responses stop the run; they are not scientific failures or successful blocking. Existing exact answers retain their original provenance and cost; cache reuse does not create new independent samples.

## Teammate return checklist

Return the reviewed challenge JSON, release SHA-256, environment identity, test logs, exclusions/disagreements and any defects. Keep the Week-4 outcome-review workbook separate. Challenge approval authorizes use of that fixture under this protocol; it does not human-verify any experiment outcome. After actual execution, support/answer adjudication, paired trade-off analysis and independent reproduction will still be required before Week6 is accepted.
