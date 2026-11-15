# GUI v2.6 — bounded testing checklist

Use the actual app/launch.py route in START_HERE.md. Keep source and ZIP pristine; write logs/screenshots/exports and notes outside the packet. This is a UI/compatibility check using the existing approved conditions, not a new efficacy study or blanket scientific acceptance.

## 1. Integrity and saved evidence

Verify the ZIP checksum sidecar, then save the output of tools/verify_packet.py before and after testing. Inspect Heather in all nine saved conditions. Confirm the selected code, reference/reproduction labels, full passages, removed original/copy decisions, actual retrieved copy counts and existing review notes. Expand review/identity sections as needed. Inspect Targeted Victory PE2, UCC BN2, test306 PN2 (retained truncation), and test1618 PN2 (both conflicting fields and the explicit discrepancy note). The automated checks cover all 531 contexts; no new manual all-531 semantic review is requested.

Check that changing a saved case or condition clears old output and disables export until new evidence is loaded. Export one saved inspection if your browser supports saving into your chosen external return folder. A saved inspection is not a live run or a new decision. Inspect the original five-section C/BN1/PN1 view and current Findings and Evidence summary as before.

## 2. Live test — nine conditions, one case

Default bounded panel: **Heather (NanoNQ:test1009), variants mode, each condition once**:

| Run | Condition | Fresh request ceiling |
| --- | --- | --- |
| 1 | C | 2 |
| 2 | BN1 | 2 |
| 3 | BN2 | 2 |
| 4 | PN1 | 2 |
| 5 | PN2 | 2 |
| 6 | BE1 | 2 |
| 7 | BE2 | 2 |
| 8 | PE1 | 2 |
| 9 | PE2 | 2 |

Nine jobs, at most 18 fresh answer attempts, **no automatic batch or retry**. Budget at most two hours for this test session; stop at that boundary even if the panel is incomplete. Preserve exact run IDs, result/state/events/console/Ollama logs and raw response files from the external runs folder. The existing code still enforces 590 seconds per response, 128 output tokens, 40 minutes per job, one active job and at most four generation attempts per job (this mode plans two). The two-hour test-session cap is a manual checklist boundary, not a new global scheduler.

For each run, confirm that selected condition and actual result condition agree; it supplies five retrieved passages, U sees all five and N sees the displayed native survivors. Compare fresh answer text with those exact passages. The digit denotes inserted copies, not a guarantee they are retrieved. No saved answer may replace a fresh failure. Preserve every output regardless of correctness. These answers need new human interpretation; historical endpoint decisions are context only.

Stop the remaining panel on fault, interruption or truncation, retain all partial files and report what did not run. Do not repeat a failed/ambiguous request to obtain preferred output. A later retry requires its own explicit disposition. Do not restart old requests 286/487 or the completed historical study.

## 3. Other controls and existing modes

The original C+PN1 mode, reviewed Week-6 mitigation panel and approved three challenge variants remain available. They are additional manual tests, not part of the default nine-job/18-answer panel. Do not silently expand the session to every case/mode. Record any extra tests and actual request/time counts separately before making claims about them.

Stop run is enabled during execution; stopping retains partial evidence and shows cancelled rather than completed. A cancellation test consumes its own explicitly identified additional job; it is not a retry of a scientific result. Use an actual additional cancellation only if you choose to extend your test plan; the release already includes synthetic start/stop/process checks. Export completed or partial snapshots; verify run ID and job status. Changing live selections clears the displayed prior result/export selection. Retain the actual run folder as the raw evidence even if the browser download is unavailable.

Do not start tools/browser_lifecycle_fixture.py for scientific/live-model testing: it is an explicitly synthetic developer test and cannot run the production backend. Only the app launch instructions start the real application.
