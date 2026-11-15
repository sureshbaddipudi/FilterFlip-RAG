# FilterFlip-RAG demo v2.3 — detailed recorded-case view

Prepared 29 October 2026. This update is for the **Inspect recorded case** screen.

## What is included

1. Question, frozen expected answer, source interpretation and recorded decision.
2. Review checks and reasoning, including the final agreed rules for jointly adjudicated cases.
3. The saved C / BN1 / PN1 answers, each with and without native filtering.
4. Expandable full passages, retrieval order, kept/removed decisions and copy identifiers.
5. Human-review dates and expandable answer call IDs and request fingerprints.

The existing visual theme remains. This is saved research evidence; new live answers still require their own review. All original evidence and review records are preserved. Where an actual date or separate checklist is not available, the screen says so; no values are invented.

## Install in your own project folder

You do not need to run this from the Codex folder. No files in your Desktop folder were changed while preparing this release.

1. If your current demo has a result on screen, use **Export this run** before closing or refreshing it. Allow an active run to finish, or stop it through the existing UI.
2. Extract `FilterFlip_Review_Demo_v2_3.zip` into your preferred project/reproduction folder as a new folder. Keep your existing release and run folders.
3. Copy your **working** `config.local.json` from your existing `FilterFlip_Review_Demo_v2_1` folder into the new `FilterFlip_Review_Demo_v2_3` folder. Copy it as a normal file, not a symlink. The ZIP deliberately contains no machine-specific configuration. Keep your existing model/input paths and your external runs folder.
4. Stop the old server with Ctrl+C in its terminal after finishing step 1. Open a terminal in the new extracted folder and run:

```bash
conda activate filterflip-core
python3 -B verify_release.py
python3 -B server.py --config config.local.json
```

5. Open http://127.0.0.1:8767 and refresh the page. The browser title should end in **v2.3**.
6. Select Heather and click **Inspect recorded case**. Read the five sections; expand PN1 under section 4 to inspect its removed copy and original biography. This check does not start model generation.

If the working configuration file is unavailable, use `config.example.json` and the path guidance in README.md. Do not run until the local configuration is ready.

## Checks and limits

The offline display check covers all 59 cases, every saved answer and passage, precedence of joint decisions, missing review forms/dates, the UCC not-applicable fields, and literal rendering of HTML-like text. Browser inspection covered Heather's decision, comparison cards and expanded PN1 copy, plus hiding an old record when the question changes. JavaScript syntax and clean-extraction release integrity passed.

Backend code, policies, input data, review records and saved evidence are byte-for-byte unchanged from v2.2. This is developer verification of the display update, not a new teammate acceptance or a fresh research run. Earlier security and research limitations still apply. No new models or experiments were run.

Optional teammate check: inspect one individual-review case (Heather), one joint case (Targeted Victory), and UCC. Report any display mismatch with the existing review. A new generation batch is not required for this update.
