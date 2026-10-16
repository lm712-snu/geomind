# Milestones (update at the end of every phase)

Last updated: Phase 2.

- [x] **Phase 1** — inspect environment; scope MVP (sandbox only: no project existed; user's local machine not yet inspected)
- [~] **Phase 2** — architecture, research protocol, acceptance criteria, CLAUDE.md
  - [x] `CLAUDE.md`, `docs/architecture.md`, `docs/research_protocol.md`, `docs/acceptance_criteria.md`, `docs/literature_notes.md`
  - [x] Literature check, 3 items (GEOBench-VLM, GeoChat, Prithvi-EO-2.0) — arXiv/model-card facts recorded
  - [ ] Licence verification for GEOBench-VLM data sources and GeoChat repo
  - [ ] Related-work search beyond the 3 items (novelty NOT yet established)
  - [ ] Local machine check (python version, free RAM/disk) — needs user output
  - [ ] User sign-off on decisions D1–D5 (defaults adopted meanwhile)
- [ ] **Phase 3** — tested vertical slice on a synthetic GeoTIFF (AT-01…AT-09)
- [ ] **Phase 4** — one analytical workflow + baseline-vs-grounded evaluation
- [ ] **Phase 5** — real pretrained model (only if it runs within compute budget)
- [ ] **Phase 6** — UI, docs, robustness, reproducibility

## Next steps
1. Run the local environment check (`python3 --version`, `free -h`, `df -h .`, `nproc`).
2. Phase 3: scaffold `pyproject.toml`, synthetic-raster generator, raster loader/validator, area functions, GeoProof schema + verifier, minimal Streamlit view — test-first.
