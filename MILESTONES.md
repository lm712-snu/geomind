# Milestones — GeoMind as the CVLM thesis application

**Purpose:** make GeoMind the applied satellite-imagery case study for the thesis [Mathematics of Computer Vision Language Models](https://github.com/lm712-snu/cvlm-thesis). The companion project explains model mathematics interactively; GeoMind connects those ideas to geospatial data, measurable evidence and controlled evaluation.

- [x] **Phase 1 — scope:** define a small, reproducible GeoMind prototype.
- [x] **Phase 2 — research design:** research question, architecture, protocol, acceptance criteria and scientific guardrails.
- [x] **Phase 3 — deterministic foundation implemented:** raster validation, area/proportion calculations, GeoProof builder/verifier, synthetic fixtures, tests and Streamlit demo.
- [ ] **Phase 4 — connect thesis mathematics:** make the companion lab and GeoMind cross-reference each other; document the actual data path from raster pixels to GIS evidence. Keep mathematical simulations clearly labelled.
- [ ] **Phase 5 — one real-data vertical slice:** choose a documented, licence-checked dataset and a bounded question type; validate metadata, nodata and spatial resolution.
- [ ] **Phase 6 — controlled CVLM experiment:** freeze a geographic holdout and independent references; compare image-only with the same VLM plus GeoProof evidence.
- [ ] **Phase 7 — evaluation and thesis write-up:** paired metrics, confidence intervals, error analysis, limitations, reproducible artifacts and viva-ready explanations.
- [ ] **Phase 8 — polished demonstration:** align the website with the actual implemented features; do not imply that an interactive globe itself performs segmentation or VLM inference.

## Acceptance gates

1. Run `pytest -q` and report the actual result.
2. Validate geographic pixel-area calculations against an independent method.
3. Confirm one real-data workflow, including licence, acquisition date, CRS, resolution and nodata handling.
4. Make an explicit diagram connecting image representation, convolution/patch embeddings, attention/cross-modal alignment, GIS evidence and answer evaluation.
5. Keep S0 image-only and S1 evidence-grounded identical except for the evidence block.
6. Use independent references; freeze prompts and scoring before the held-out test.
7. Publish no accuracy or improvement claim until the experiment has actually been run.
