# TrustRAG embedding label correction in v2.9.3

MiniLM retrieved the five passages. TrustRAG stage 1 uses saved CPU embeddings from `princeton-nlp/sup-simcse-bert-base-uncased` (revision `2d82fab19ac3a73a20dd20333d27eb8a52d6e97f`). The GUI now displays SimCSE and labels new exports `frozen_simcse_cpu`. Historical run exports retain their recorded labels.

The embedding array is byte-identical to the original component run and the v2.9.1 GUI. Its SHA-256 is `08b269ace94776febb44384c98e117078bae7967ceca83d880795c8d73b482e4`. The archived source binding records the model revision and array digest. Its original scope description contains the earlier Contriever label.
