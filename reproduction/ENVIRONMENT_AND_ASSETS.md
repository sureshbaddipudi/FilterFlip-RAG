# Existing environment and external assets

The default Task-13 saved-data checks need no model assets, original package paths or installation. Standard Python handles most checks; an existing Python with NumPy handles the corrected comparator; an existing Node handles two JS checks. All missing-tool outcomes must remain NOT_RUN. The original requirements file is historical metadata, not an instruction to upgrade the accepted environment.

## Frozen inference profile — reference only

| Item | Identity retained |
|---|---|
| Native pipeline | RAGDefender 0.2.0; CPU; single hop; m=5, p=2; top-five retrieval |
| Encoder | sentence-transformers/all-MiniLM-L6-v2; snapshot 1110a243fdf4706b3f48f1d95db1a4f5529b4d41 |
| Answer model | Qwen2.5:3b, Ollama 0.34.2 |
| Digest | 357c53fb659c5076de1d65ccb0b397446227b71a42be9d1603d46168015c9e4b |
| Template SHA-256 | eb4402837c7829a690fa845de4d7f3fd842c2adee476d5341da8a46ea9255175 |
| Answer options | temperature 0, seed 42, context 4096, maximum output 128 tokens |
| Baseline distributions | sentence-transformers 5.1.0; transformers 4.51.3; torch 2.8.0+cpu; numpy 2.4.6; scikit-learn 1.9.1 |
| Mitigation | U/N/E/CN; CN threshold 0.95; evaluated ordering/singleton bypass retained |

The exact MiniLM file hashes are in baseline/original_metadata/models.json and Task-12 result identities. Each new original-task inference used its own bounded plan and identity checks. The isolated candidate is separate and **not adopted**; never substitute its environment in the baseline demo or relax frozen profile checks.

For any separately requested later live deployment, reuse the existing extracted FilterFlip_Reproduction_Package, pinned environment, encoder cache and model store. The six absolute config paths are machine-specific: python, package, encoder, ollama_binary, ollama_models and a new private runs folder. See components/task12/app/config.example.json. Do not reuse completed ledgers, copy Ollama private keys, write inside code/model/input trees, or download models merely to inspect saved results. No private key, installed environment or model weight is bundled.

The model-disabled verification helper requires none of those six real assets. Its synthetic UNUSED_* paths are deliberate placeholders, never a usable inference configuration. Its server-side start/cancel overrides prevent model requests. The production source remains unchanged.

No public host, proxy/tunnel or multi-user deployment is part of this handover. Mapping applicability, passing tests and byte-identical outputs do not close every security risk or establish general safety. Advisory records remain dated evidence; no new online scan is claimed.
