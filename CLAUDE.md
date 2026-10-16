# CLAUDE.md — GeoMind project instructions

GeoMind: *From Satellite Imagery to Verifiable Geospatial Intelligence.* Signature capability: **GeoProof**, an evidence ledger that makes geospatial AI answers traceable, measurable, and reproducible.

Research question: does grounding vision-language model responses in explicit GIS measurements and geospatial provenance improve factual accuracy and spatial consistency compared with image-only responses?

## Non-negotiable rules
1. Inspect the repository and environment before changing files.
2. Build the smallest complete slice; implement, run, test, then continue.
3. Never fabricate datasets, models, APIs, metrics, maps, test results, or findings. If a command was not run, say so.
4. Numerical answers come from deterministic code. A language model may plan or phrase, but cannot invent measurements.
5. Abstain or ask for clarification when evidence is missing or invalid.
6. A visual heuristic is never called a trained model. Mapped-class change is not automatically real-world change. Confidence is not called calibrated without evaluation.
7. Provenance is not proof. GeoProof records calculation lineage; verification must recompute claims.
8. Never execute generated code or shell commands. Tools must be explicitly allowlisted and arguments validated.
9. Verify dataset/model licences, API terms, compute requirements, and commercial-use limits before integration.
10. Do not suppress errors to make a demo look successful.

## Environment constraints
Target machine: 8 GB RAM, Intel i3, limited SSD. Keep the core CPU-first and support small samples. Heavy inference is optional and must be isolated behind an adapter. The deterministic core must not require a paid API.

## Current structure
- `src/geomind/raster.py`: raster metadata, validation, alignment.
- `src/geomind/analysis.py`: deterministic area/proportion calculations.
- `src/geomind/proof.py`: GeoProof schema, builder, verifier.
- `app/main.py`: minimal Streamlit synthetic-data demo.
- `tests/`: generated fixtures and automated tests.
- Root-level `architecture.md`, `research_protocol.md`, `literature_notes.md`, and `acceptance_criteria.md` document the research plan.
- `MILESTONES.md` tracks actual progress.

## Commands
```bash
python -m pip install -e ".[dev]"
pytest -q
streamlit run app/main.py
```
Windows PowerShell virtual environment activation: `.venv\Scripts\Activate.ps1`. macOS/Linux: `source .venv/bin/activate`.

## Mathematical conventions
- Exclude nodata and invalid pixels; zero valid area means the proportion is undefined.
- Projected area uses affine determinant and CRS axis unit conversion.
- Geographic pixel area varies by latitude; the current row-wise method assumes a north-up grid and rejects rotated geographic grids.
- Percentage-point change is distinct from relative percentage change.
- Compare dates on common valid coverage before interpreting change.
