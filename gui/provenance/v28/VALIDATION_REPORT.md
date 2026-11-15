# GUI v2.8 verification

10 November 2026. New-version developer verification; independent acceptance remains pending. No research models were loaded or called. All original results and attributed reviews remain preserved.

| Check | Result | Scope |
|---|---|---|
| Starting v2.7.2 packet | 383 listed files match | Original release read only |
| Preservation | 132 existing data/policy/profile files byte-identical | New findings display data is additional; source copies and bindings retained |
| Scientific request contract | Unchanged | Model, digest, prompt, generation options, port, request and response-status functions; backend diff retained |
| Application Python suite | 68 pass normally; same 68 pass with -O | Existing 50 plus 18 config, verified-loading, audit, archive, findings and HTTP regression tests |
| Additional security suite | 15 pass normally; same 15 pass with -O | Admission limits, handlers, headers, paths, IDs, links, input and response contracts |
| JavaScript checks | Five suites pass | All 59 historical cases, 531 case-condition views, 118 overview views, 1,062 focused views, selection identity, controls and export |
| Chrome UI and HTTP checks | 10 pass | Saved navigation, 12 TrustRAG cases/72 answer positions/180 passage positions, hostile text, mobile width, synthetic start/cancel/download |
| Packet diagnostics | Five checks pass | Clean, missing, modified, unexpected and linked files |
| Static production Python scan | One medium, seven low; zero scan errors | Explicit dispositions in SECURITY_REVIEW.md; raw scanner JSON retained |

Normal and optimized executions repeat the same test suites; do not add them as independent security properties. The deliberate audit-symlink negative test emits a logging-unavailable warning: this is expected. Earlier supplementary test expectations were adjusted because strict extra-field cancellation now returns 400 and new operational lock/log files legitimately exist; current logs record the passing reruns. Browser output uses a synthetic worker. It does not validate new Qwen answers or establish model security.

## Reproduce the offline checks

From the extracted release root, use your existing filterflip-core environment:

```bash
python3 -B tools/verify_packet.py
python3 -B -m unittest discover -s app/tests
python3 -O -B -m unittest discover -s app/tests
python3 -B tools/check_additional_security.py .
python3 -O -B tools/check_additional_security.py .
node tools/check_controls.cjs
node tools/check_presentation.cjs
node tools/check_gui_identity.cjs
node tools/check_saved_conditions.cjs
node app/validation/check_recorded_view.cjs
```

Python tests need temporary localhost sockets. Node tests need an installed Node runtime. Neither set calls research models. Browser checks additionally require an existing Playwright installation and Chrome; set PLAYWRIGHT_MODULE to its module path, TEST_PYTHON to your interpreter and optionally CHROME_BINARY. Give an output folder outside the release:

```bash
mkdir -p "$HOME/FilterFlip_v28_browser_check"
node tools/check_browser.cjs . "$HOME/FilterFlip_v28_browser_check"
```

The browser harness uses a disposable synthetic worker and blocks requests to other origins. Its temporary files and screenshots are software-test evidence, not research observations. The bundled screenshots illustrate the recorded findings layout and saved evidence.

## Scope and remaining checks

New-version real model acceptance has not been run. Prior live-mode operation is historical evidence only; the byte-preservation check and software tests reduce regression risk without replacing a fresh end-to-end acceptance. Follow ACCEPTANCE_CHECKLIST.md for independent review. Hard OS quotas, long-duration/full-budget stress, public deployment, dependency remediation and broad model-security claims remain outside this release. No historical research experiment was repeated.

The source and application manifests are regenerated after documentation is sealed. External RELEASE_VERIFICATION records the packet and ZIP verification; the ZIP checksum is alongside it. Current evidence lives in validation/v28; other validation folders remain dated historical records.
