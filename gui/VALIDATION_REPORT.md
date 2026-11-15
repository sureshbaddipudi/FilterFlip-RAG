# GUI v2.9 validation report

10 November 2026. Developer verification of the new release. Independent v2.9 acceptance and semantic review of its new answers remain pending. Historical human reviews are unchanged.

| Check | Result | Scope |
|---|---|---|
| Original v2.8 source | 441 manifest files verified | Original source and Desktop folders untouched |
| Frozen preservation | See PRESERVATION.json | All existing app/data files, policies and native profile byte-identical; four-mode retrieval/filter body unchanged after indentation |
| Application tests | 81 pass normally and with Python -O | Same suite repeated in two modes; Trust scope, fixed-data isolation, output ordering, empty context, tampering, input budgets and HTTP routes included |
| Additional security probes | 15 pass normally and with -O | Local handlers, limits, invalid fields/IDs, framing, links and response contracts |
| JavaScript checks | Five suites pass | Historical 59 cases, 531 condition views, 118 overviews/1,062 focused views, identity, literal rendering and controls |
| Real browser | 14 checks pass | New project/Trust views, mobile layout, literal hostile text, synthetic start/cancel/reconnect/export and recorded-case routing |
| Fresh Trust filter | 36/36 original contexts match | Actual native filtering on saved embeddings, exact kept order/output; no answer model in this check |
| Real integration | Three completed runs, six fresh responses | Cornflakes PN1, cornflakes C reorder, signal-transduction C empty output; actual Manager/HTTP/worker/Qwen path |
| Static scan | One medium, seven low; zero scan errors | Production app code including native filter, excluding tests and separately inventoried vendored runtime; explicit dispositions in SECURITY_REVIEW.md |
| New support-runtime lookup | 73 raw rows / 41 NLTK advisory groups | Four pinned support packages queried; open findings, not a clean scan or complete tree audit |

No full research panel was regenerated. The three integration runs are software verification, not accepted new research results. Request hashes and raw responses are retained in validation/v29/live_runs. The saved study remains the scientific record. A separate first harness attempt expected HTTP 200 rather than the actual accepted-start HTTP 202; it was cancelled with zero generation attempts and is retained. The browser's initial wait used a hidden compact heading in detailed mode; the selector was corrected, with that attempt retained. Socket/DNS restrictions affected other first attempts before the required permission was available. The intentional audit-link test emits a logging-unavailable warning. None of these histories are silently erased.

The final text bounds were added after the six generation calls. All 36 contexts pass those bounds, the final filter-equivalence check still matches all selections and the final application/browser suites pass. No additional Qwen repeat was necessary: request building and generation were unchanged by the input-bound check.

## Reproduce software checks

From the extracted release root in filterflip-core:

```bash
python3 -B tools/verify_packet.py
python3 -B -m unittest discover -s app/tests
python3 -O -B -m unittest discover -s app/tests
python3 -B tools/check_additional_security.py .
python3 -O -B tools/check_additional_security.py .
python3 -B tools/check_trust_filter.py
node tools/check_controls.cjs
node tools/check_presentation.cjs
node tools/check_gui_identity.cjs
node tools/check_saved_conditions.cjs
node app/validation/check_recorded_view.cjs
```

The Python suites need temporary localhost sockets. The Trust filter check uses the existing pinned numerical environment and bundled verified support libraries, but loads no encoder or answer model. It compares against the recorded expected selection only in this verification tool; the live branch does not consume that expected mask.

Browser checks need an existing Playwright installation, Chrome and Node. Set PLAYWRIGHT_MODULE to the module path, TEST_PYTHON to the interpreter and optionally CHROME_BINARY, then run `node tools/check_browser.cjs . /absolute/path/to/new-browser-output` after creating that external output directory. Its worker is synthetic; it never starts Qwen. Model-backed acceptance is separately described in ACCEPTANCE_CHECKLIST.md and should export its own runs.

## Limits

No general security certification, new human correctness judgments, full TrustRAG result, broad population attack rate, generally effective mitigation, candidate-environment adoption or complete dependency remediation. The new read-only report is still a draft. Vendor source inventory/identity and selected bounded execution do not establish that all advisory paths are closed. See current security documents and the source bindings for qualifications.
