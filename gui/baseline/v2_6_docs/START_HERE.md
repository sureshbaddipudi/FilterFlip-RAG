# FilterFlip-RAG GUI v2.6 — live testing of all nine conditions

3 November 2026. This is the **live-capable application**, supplied separately in response to Suresh's request. Start it with app/launch.py or app/server.py. It does not use tools/serve_readonly_gui.py. The earlier read-only helper was for saved-evidence verification and deliberately blocked generation; it was not suitable for testing live computation. This supplement leaves the Task-13 v1.1 handover and every earlier package unchanged.

## Start the actual GUI

Extract this new GUI ZIP into a separate folder. Reuse your existing original package, cached model assets and pinned CPU environment; do not re-extract the original reproduction package or install dependencies. Run these commands from this new GUI packet's root. Replace the two uppercase example paths with your existing configuration and a new private test folder outside the extracted packet:

```bash
python3 -B tools/verify_packet.py
python3 -B app/configure.py --from-config /ABSOLUTE/PATH/TO/YOUR/EXISTING/config.local.json --work /ABSOLUTE/PATH/TO/NEW/FilterFlip_v26_test
python3 -B app/launch.py /ABSOLUTE/PATH/TO/NEW/FilterFlip_v26_test/config.local.json
```

The helper copies only the five existing asset/interpreter paths, sets the CPU profile and creates a separate private runs folder. It does not change the old configuration, install anything, or start a model. Backend inference uses the pinned Python path inside that configuration. If an existing asset path is missing on this machine, correct your **external** configuration using app/config.example.json; do not edit sealed app files. Existing configuration can come from your prior working demo, not the read-only helper's UNUSED-path configuration.

Open **http://127.0.0.1:8767**. The badge should read **Local CPU · Fresh inference**, without a read-only notice. Run live comparison should be enabled. Stop run becomes enabled only while a job is active; Export this run becomes enabled once a run snapshot exists. These normal initial button states do not mean models are disabled.

If 8767 is occupied, stop your own previous demo or use another free localhost port:

```bash
python3 -B app/server.py --config /ABSOLUTE/PATH/TO/NEW/FilterFlip_v26_test/config.local.json --port 8770
```

Only a manual click on Run live comparison starts fresh inference. The dedicated model port remains 11437; an unrelated service is not stopped automatically. Shut down the app with Ctrl+C after testing. Its owned worker is cancelled and partial evidence remains in your external runs folder.

## What to test

- **Live demonstration → All nine conditions · native filter comparison:** all 59 existing cases and C, BN1, BN2, PN1, PN2, BE1, BE2, PE1, PE2. Each click retrieves the selected condition, runs the unchanged native filter, and generates two fresh answers (U and N). It is one selected condition per run, not an automatic 531-context experiment.
- **All nine saved conditions:** all 59 × 9 contexts, both saved reference and later reproduction answers, full retrieved passages, kept/removed decisions, inserted/retrieved copy counts, existing secondary reviews and linked response reviews. No model is run by this tab. Its separate export is labelled recorded_study_inspection.
- **Original finding:** existing C+PN1 paired mode, four fresh answers.
- **Week-6 mitigation:** existing reviewed benign panel, C/BN1/PN1 and U/N/E/CN, four fresh answers. Secondary conditions have not been added to CN evaluation or declared approved mitigation evidence.
- **Security challenge:** existing approved neutral, false-claim and instruction fixtures, four fresh answers. This remains forced six-passage exposure, not a fresh retrieval attack.
- **Inspect recorded case:** retains the original five-section primary review, attribution and all C/BN1/PN1 saved evidence.

Read TEST_PLAN.md for the bounded nine-condition check and RETURN_GUIDE.md for files to retain. No new human judgments are prefilled. Fresh answers are not expected to reproduce every historical wording, and they do not inherit old endpoint labels. Negative results, truncations, uncertainty and partial outputs must remain visible.

## State of this release

Software and browser checks are described in VALIDATION_REPORT.md. No encoder/model was loaded and no research answer was generated during preparation. Actual new-machine inference/answer interpretation remains your live test, not a claimed completed run. Existing research inputs, policies.py, fixed model/prompt/options, scientific labels and the original handover remain unchanged. Full TrustRAG generation, larger data, broad sweeps and new mitigation research remain outside this GUI change.

This is a GUI supplement, not a replacement Task-13 offline handover. Keep the original v1.1 ZIP/checksum and its forms. Task 13 stays open while verification and final acceptance are pending; the report still awaits Suresh's review and presentation remains deferred.
