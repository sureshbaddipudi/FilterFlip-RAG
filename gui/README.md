# FilterFlip-RAG GUI v2.9.3

**Reviewed by Shradha** (semester GUI v2.9). Suresh and Shradha accepted the GUI for the semester demonstration on 14 November 2026.

Version 2.9.1 corrects the byline of the [v2.7.2 security assessment](review_input/SHRADHA_V272_ASSESSMENT.md) and identifies the reviewed GUI here.

## Verify and run

Activate the filterflip-core environment and open a terminal in the extracted folder. With the existing private v2.9 configuration, run

```bash
python3 -B tools/verify_packet.py
python3 -B app/launch.py "$HOME/FilterFlip_v29_work/config.local.json"
```

If your external configuration is elsewhere, supply its actual path. For first-time setup, see the [setup guide](START_HERE.md).

## TrustRAG embedding correction

MiniLM retrieved the five passages. TrustRAG stage 1 uses saved CPU embeddings from `princeton-nlp/sup-simcse-bert-base-uncased` (revision `2d82fab19ac3a73a20dd20333d27eb8a52d6e97f`). The GUI now displays SimCSE and labels new exports `frozen_simcse_cpu`. Historical run exports retain their recorded labels.

See the [embedding verification note](provenance/V293_EMBEDDING_LABEL_CORRECTION.md). The archived review records retain their v2.9.1 contents. The [original dependency scan](provenance/DEPENDENCY_AUDIT_as_received.json) accompanies the [display copy](app/validation/DEPENDENCY_AUDIT.json).
