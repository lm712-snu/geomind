# Milestones

Last updated: Phase 3 scaffold committed; local execution not yet verified.

- [x] **Phase 1** — inspect repository metadata and scope MVP. The user's local machine has not been inspected.
- [x] **Phase 2** — research question, architecture, research protocol, acceptance criteria, coding-agent instructions.
- [~] **Phase 3** — first vertical slice implemented in the repository; acceptance tests still need to be run in CI or a local environment.
  - [x] Project packaging, dependencies, ignore rules, and README.
  - [x] GeoTIFF inspection and grid-alignment validation.
  - [x] Deterministic class-area calculation with valid-pixel masking.
  - [x] Projected and geographic pixel-area handling.
  - [x] GeoProof schema, JSON round-trip path, and arithmetic verifier.
  - [x] Synthetic fixtures and tests for area, nodata, CRS, alignment, and tampering.
  - [x] Minimal Streamlit demonstration.
  - [ ] Run automated tests and fix any failures; no test result is claimed yet.
  - [ ] Verify geographic pixel-area results against an independent calculation.
  - [ ] Confirm AppTest smoke test and CI status.
- [ ] **Phase 4** — one real-data workflow + baseline-versus-grounded evaluation.
- [ ] **Phase 5** — real pretrained model, only if model requirements/licence/compute are verified.
- [ ] **Phase 6** — polished UI, robustness, documentation, reproducibility.

## Next steps
1. Check the GitHub Actions workflow result and fix any actual failures.
2. Run locally: `python --version`, `python -m pip install -e ".[dev]"`, then `pytest -q`.
3. Review the synthetic workflow with the supervisor before selecting a real dataset.
4. Complete dataset/model licence verification and related-work search before making novelty claims.
