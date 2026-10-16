# Literature notes (Phase 2 — partial)

**Novelty is NOT established.** Only three items were checked. A focused related-work search (tool-augmented / agentic geospatial LLMs, provenance and evidence-grounded answering for remote sensing, remote-sensing VQA benchmarks) is still required before any novelty claim.

Source quality: P = primary (arXiv, official model card); S = secondary (third-party summary — treat as a lead to confirm).

## GEOBench-VLM
- arXiv 2411.19325, Danish et al.; ICCV 2025 (P).
- Benchmark for VLMs on geospatial tasks; over 10,000 manually verified instructions; scene understanding, counting, localization, fine-grained categorization, segmentation, temporal analysis (P). Version 1 figure caption: 31 fine-grained tasks in 8 categories (P).
- ICCV abstract reports the best model, LLaVA-OneVision, at 41.7% MCQ accuracy, slightly above GPT-4o (P; abstract wording differs between versions — cite the version used).
- Repo: github.com/The-AI-Alliance/GEO-Bench-VLM. **Licence of repo and of the underlying source datasets: NOT verified.**
- Use for GeoMind: related work and possibly question formats; not assumed to fit our GeoTIFF-measurement setting.

## GeoChat
- arXiv 2311.15826, Kuckreja et al.; CVPR 2024 (P). Grounded remote-sensing LVLM fine-tuned from the LLaVA-1.5 architecture; image/region captioning, VQA, scene classification, grounded conversation, referring detection (P).
- Hugging Face card for MBZUAI/geochat-7B lists licence Apache-2.0 (P). A secondary summary says the GitHub README does not state a licence explicitly and notes dependence on LLaVA/Vicuna (S) — **repo licence and inherited terms (LLaVA, Vicuna, training data) to be verified.**
- Secondary summary: CLIP ViT-L/14 + MLP projector + Vicuna-1.5; ~25 h training on 3×A100 (S).
- Compute: a 7B model in fp16 needs about 14 GB for weights alone (7×10⁹ params × 2 bytes) — more than the 8 GB local RAM. Local inference is not feasible without quantization; evaluate on Colab or skip (decision in Phase 5).

## Prithvi-EO-2.0
- arXiv 2412.02732, Szwarcman et al. (P). Geospatial foundation model, 300M and 600M parameter variants, trained on 4.2M global time-series samples from NASA's Harmonized Landsat and Sentinel-2 archive at 30 m (P). Reported: 600M variant outperforms Prithvi-EO-1.0 by 8% across GEO-Bench tasks (P, authors' own benchmarking).
- Hugging Face cards (ibm-nasa-geospatial/Prithvi-EO-2.0-600M and -300M-TL) list Apache-2.0; available on Hugging Face and IBM TerraTorch (P).
- It is a pretrained **encoder/foundation model**, not a conversational VLM. Using it requires a task head or embedding pipeline; input requirements (bands, temporal frames, 30 m HLS-like data) and CPU feasibility are **not yet verified**.

## To do
- [ ] Verify licences/terms: GEOBench-VLM repo + sources; GeoChat repo, LLaVA/Vicuna terms.
- [ ] Related-work search for novelty positioning.
- [ ] Read the benchmark papers' evaluation protocols to align metrics where sensible.
