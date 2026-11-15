# FilterFlip-RAG GUI v2.9.3 — start here

See [README.md](README.md) for the 14 November 2026 documentation update and existing-configuration launch instructions. The underlying v2.9 release was built on 10 November 2026 with live TrustRAG stage-1 comparison and an overview of the completed project work. Earlier releases are preserved.

## Run from your own extracted folder

Stop your previous GUI with Ctrl+C. Extract this ZIP into a new folder and open a terminal there. **Do not put config.local.json inside the extracted release.** Reuse the external private configuration prepared for v2.8 to create a new work folder:

```bash
conda activate filterflip-core
python3 -B tools/verify_packet.py
python3 -B app/configure.py --from-config "$HOME/FilterFlip_v28_work/config.local.json" --work "$HOME/FilterFlip_v29_work"
python3 -B app/launch.py "$HOME/FilterFlip_v29_work/config.local.json"
```

If your working config is elsewhere, replace the --from-config path with that actual path. The new work folder must not already exist. The helper reuses model/input locations, creates a private config and new runs folder, and never overwrites the old work. No models or packages are downloaded by setup. The existing pinned CPU environment and local assets are required.

Open **http://127.0.0.1:8767** and refresh. For subsequent starts use the environment activation and last launch command only. Use Python -B to keep bytecode out of the sealed application folder. Stop the GUI before offline archiving; see ARCHIVE_GUIDE.md.

If your extraction tool creates group-writable directories, remove group/other write permission on this new release folder only (`chmod -R go-w .` while standing in its root). The ZIP stores directories as 0755 and ordinary files as 0644, but extraction behavior varies. Keep the checksum outside the release; packet verification rejects extra files.

## What to open

- **Live demonstration:** original comparison, all nine native-filter conditions, mitigation, security challenges, and now TrustRAG stage 1.
- **All nine saved conditions:** exact reference/reproduction passages, answers and recorded reviews.
- **Findings and Evidence:** primary, copies, reproduction, mitigation, challenges, recorded TrustRAG and security limitations.
- **Project work and security:** the 13 later tasks, earlier milestone summary, supporting records, STRIDE and four OWASP mappings, dependency compatibility work, literature positioning, and the semester report draft.

## First TrustRAG walkthrough

Choose **TrustRAG stage 1 · fixed contexts, fresh filter and answers**. Select **who invented corn flakes**, then **C** and click Run live comparison. Read U (no filter) and T (TrustRAG stage 1), including the order of the passages supplied to each answer. Export the run. Repeat with **PN1** and inspect the removed answer passage and copy. Fresh answers may differ; interpret them against the surviving evidence and the archived-source qualification.

This mode uses the original saved five-passage contexts and verified saved SimCSE embeddings. It **runs the original stage-1 clustering/ngram filter now and generates two fresh Qwen answers**. Retrieval and embedding generation are not rerun. It does not replay saved answers or reuse saved kept masks. Twelve original questions and C/BN1/PN1 are available. Later TrustRAG stages are not implemented.

Inspect recorded case opens the matching saved TrustRAG record, not a native-filter verdict. Saved reviews never become judgments of the new answers automatically.

Read VALIDATION_REPORT.md for developer checks, SECURITY_REVIEW.md for remaining risks, and ACCEPTANCE_CHECKLIST.md for independent review. The v2.9 GUI was accepted for the semester demonstration on 14 November. Fresh answers require their own review.
