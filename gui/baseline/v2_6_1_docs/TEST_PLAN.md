# GUI v2.6.1 — bounded display verification

This correction changes display identity and request handling. Tasks 12 and 13 remain jointly accepted for their exact recorded scope. No repeat of the previous nine-job live panel, twenty-answer review or full handover return is requested.

1. Verify the ZIP checksum and run `python3 -B tools/verify_packet.py` before and after testing. Write test material outside the packet.
2. Open the normal live-capable app. Confirm v2.6.1 in the title, four live modes, nine conditions in variants mode and 59 questions. Inspect recorded Heather, then change question/condition: the old panel must close. With a delayed reply, the old case must not reopen. Run the synthetic check below to reproduce that timing deterministically without model calls.
3. Confirm Findings and Evidence reports Tasks 12 and 13 jointly accepted on 5 November; the older v2.4 decision stays scoped, and the report still awaits Suresh’s review. Check all-nine saved views, full passages and recorded reviews as before; no answers are relabeled.
4. Run the deterministic reconnect/race checks with your existing Node installation: `node tools/check_gui_identity.cjs`. They simulate an active non-default question/mitigation/BN1 run, reload, completion/export, delayed inspections and a superseded poll. They cannot run a model or create a real research result. Preserve their output as software-test evidence.
5. A real active-job reload may be checked during a separately intended demonstration: verify question, ID, mode and condition match its state/export. Do not start a model job solely to repeat this display check. Any additional fresh generation remains a separately counted run under existing limits, without automatic retry or inherited judgments.

Record any visual discrepancy and actual browser details. A browser save dialog and fresh-model execution were not exercised for this correction. No new semantic judgment or required return package is prefilled. Prior v2.6 testing guidance is retained as historical documentation in baseline/v2_6_docs.
