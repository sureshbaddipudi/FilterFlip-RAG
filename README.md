# FilterFlip-RAG

M.Tech Secure Software Engineering project, IIT Hyderabad  
Suresh Kumar Baddipudi and Shradha Suryawanshi

Can adding a copy of a passage that contains the correct answer cause a RAG security filter to discard the evidence needed to answer a question? We compared retrieved passages, filter decisions and answers with and without filtering. The primary review identified eight events in 59 selected cases. The separate TrustRAG stage-1 study found five events, six non-events and one uncertain case among twelve selected questions.

Start with the [baseline study](research/baseline/README.md) for the research question, comparison conditions, datasets and software versions.

## Reproduce the study figures

From the repository root, use Python 3 with Matplotlib installed and choose a new output directory.

```bash
python3 reproduction/components/paired-results-analysis/code/plot_results.py --out figures-local
```

Open `figures-local/copy_exposure_endpoints.png` to see how many copies reached retrieval and how the reviewed outcomes changed across conditions. Open `figures-local/trustrag_support_core.png` to compare evidence support and answer usability for all 36 paired contexts. Each figure is also available in SVG format.

The [saved summaries](reproduction/components/paired-results-analysis/expected/) come from the semester paired analysis. The plotting script and four summary files are copied from that analysis. The TrustRAG context file includes only the case ID, condition and four recorded judgment fields used by the figure. Plotting uses the recorded labels and performs no model calls.
