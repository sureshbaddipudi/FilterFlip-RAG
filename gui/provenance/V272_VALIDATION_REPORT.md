# GUI 2.7.2 final verification

9 November 2026. All listed verification targets this corrected release. Logs and reproducible boundary checks are in the accompanying FilterFlip_Final_Security_Review_2026-11-09 package.

| Check | Result |
|---|---|
| Application suite in filterflip-core | 50 pass normally and the same 50 pass with -O |
| Additional security probes | 15 pass normally and the same 15 pass with -O |
| Existing JavaScript interface suites | Five pass |
| Real Chrome browser | Saved navigation, hostile-text literal display and synthetic start/cancel/export pass |
| Static Python scan | Seven low alerts reviewed, zero medium/high, zero scan errors |
| Dependency inventory/query | 43 packages, 92 raw records, 81 component/advisory clusters open |
| Research model inference | Zero calls |

An initially failing null-cancellation check motivated the server fix. The existing live cancellation path still passes both process lifecycle and browser tests. The browser uses the actual packaged frontend and HTTP server with an explicitly synthetic worker, and never substitutes its output for research evidence. This is engineering verification rather than a new scientific judgment.

The complete scope, earlier restricted attempts, first browser locator adjustment and limitations are recorded in the companion review. The original release and source evidence remain separately available.
