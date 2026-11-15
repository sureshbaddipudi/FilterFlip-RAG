# FilterFlip live demo v1 — teammate acceptance return (draft)

Tester: Shradha. Date: 23 October 2026. Release: `FilterFlip_Post_Review_Development_Handover_2026-10-22` (outer ZIP SHA-256 `a33acf2537d1f2ba7b077ec34cdbd012cb4d164d6102138e7f64c7de06bea69f`). Testing was assisted by Claude Code. The answer judgments in row 15 are my own decisions; the review is unblinded and not a joint adjudication.

## Environment

- Ubuntu (Linux 6.8), 12 CPU threads, 31 GB RAM, Quadro K420 GPU (Vulkan driver NVK).
- Python env named `filterflip-repro` (3.11); named `filterflip-core` in the docs. Package versions match `native_profile.json`: torch 2.8.0+cpu, sentence-transformers 5.1.0, transformers 4.51.3, numpy 2.4.6, scikit-learn 1.9.1, ragdefender 0.2.0.
- Ollama 0.34.2; `qwen2.5:3b` ID `357c53fb659c`; MiniLM snapshot `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`.
- `config.local.json` rewritten with my paths. Ollama run with `OLLAMA_VULKAN=0 OLLAMA_LLM_LIBRARY=cpu CUDA_VISIBLE_DEVICES=-1` (see issue 1).
- `~/.ollama` did not exist at the start and was created with `mkdir -p`.

## Results

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | `verify_release.py` | Pass | 26 release files verified |
| 2 | Outer `PACKAGE_MANIFEST.json` | Pass | 39 of 39 files match |
| 3 | Unit tests, normal and `-O` | Pass | 19 of 19 each |
| 4 | Heather C/PN1 live run, default GPU settings | **Fail (environment)** | Runs `7f03a461…` and `407e628b…`: Vulkan device lost; 0 answers; no retry or substitute answer |
| 5 | Heather C/PN1 live run, CPU forced | Pass | Run `af0c3764…`: 4 answers, all `ok`, finish reason `stop`, about 91 s |
| 6 | Request hashes vs recorded reference | Pass | All four match |
| 7 | Retrieved passages and kept indices vs reference | Pass | Both conditions match |
| 8 | Answer text vs recorded reference | Pass | All four identical to the reference (the 19 Oct run differed by "&" vs "and" in one answer) |
| 9 | Stop run, early | Pass | Run `2551764c…` cancelled, partial files kept, no listener on 11435 |
| 10 | Stop run, during generation | Pass | Run `7c72846a…` cancelled while generating; no listener on 11435 and no Ollama process other than the system service; timing of cleanup not measured |
| 11 | Second job refused | Pass | "One live comparison is already running" from a separate Incognito session |
| 12 | Occupied dedicated port 11435 | Pass | Run `1656e411…` failed "Dedicated Ollama port already in use"; no answers generated |
| 13 | Recorded evidence, Heather, view and export | Pass | Earlier assessment, assistant rationale and Shradha's review all present and separated |
| 14 | Recorded evidence, Targeted Victory, view and export | Pass | Historical assessment and Shradha's decision (disagreeing with "Needs adjudication") present in view and JSON |
| 15 | Semantic review of fresh answers (run `af0c3764…`) | Done by tester | Clean/unfiltered, clean/filtered and copy/unfiltered: correct and supported. Copy/filtered ("Not enough information."): strict event = yes (support lost after filtering, only the cast-list name survives; abstention). Same reading as the 14 Oct review of the recorded evidence; not jointly adjudicated. |
| 16 | Repeat Heather run `785cef1c…` (started by tester; completed, about 75 s) | Pass | Same four answers as `af0c3764…`; not independently compared by hash |

## Issues

1. **GPU crash on default settings.** Ollama picked the Vulkan device (Quadro K420) and crashed with `ErrorDeviceLost` on the first request; the demo stopped safely as designed. Forcing CPU fixed it. Suggest the README document a CPU-only option for machines with weak GPUs.
2. **Env name differs.** `filterflip-repro` here vs `filterflip-core` in the docs; no functional effect because the config holds the interpreter path.
3. **Broken editable install.** The env's `ragdefender` editable install points to a path that does not exist on this machine. No effect, because the backend loads the vendored copy by hash.
4. **Cancelled run `9fc6d5ad…`.** A run started during the second-job test was cancelled after about 31 s, during generation of the first answer; it did not finish. It was the active run when I stopped the server with Ctrl+C, which the README says stops an active run; partial evidence kept.
5. **Not tested:** other 58 questions, the BN1 option, concurrent load, and a timing measurement of listener shutdown.

## Run folders retained

`FilterFlip_Live_Demo_Runs/`: `7f03a461…` (GPU crash), `407e628b…` (GPU crash), `af0c3764…` (good run), `2551764c…` (early stop), `7c72846a…` (stop during generation), `785cef1c…` (second completed run), `9fc6d5ad…` (cancelled during generation, see issue 4), `1656e411…` (occupied port). Exported result: `FilterFlip_af0c3764b2e543b588e5d9723a09c482.json`; recorded-evidence exports for Heather and Targeted Victory.

No Ollama private keys are included.
