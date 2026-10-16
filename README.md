# GeoMind
**From Satellite Imagery to Verifiable Geospatial Intelligence**

GeoMind is a research prototype for asking questions about geospatial imagery and receiving answers tied to reproducible GIS evidence. Its signature feature, **GeoProof**, records the data, operations, measurements, assumptions, and verification status behind each answer.

> **Status:** early research scaffold. The first milestone is a tested synthetic GeoTIFF workflow. No pretrained model, real-world change-detection result, or research finding is claimed yet.

## Research question
Does grounding vision-language model responses in explicit GIS measurements and geospatial provenance improve factual accuracy and spatial consistency compared with image-only responses?

## Current MVP
- Validate GeoTIFF CRS, transform, dimensions, nodata, and alignment.
- Calculate class area and class proportion using valid pixels.
- Create a structured GeoProof record with transparent calculation inputs.
- Recompute recorded area from per-row counts and pixel areas.
- Explore the result in a lightweight Streamlit interface.
- Test edge cases with synthetic data whose expected values are known.

## Quick start
Python 3.11 or 3.12 is recommended. Geospatial wheels can vary by operating system.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest -q
streamlit run app/main.py
```

The app creates a small synthetic raster for demonstration. **It is synthetic data, not a satellite observation.**

## Repository guide
- `src/geomind/raster.py` — raster metadata and alignment validation
- `src/geomind/analysis.py` — area/proportion calculations
- `src/geomind/proof.py` — GeoProof schema, builder, verifier
- `app/main.py` — minimal demo interface
- `tests/` — tests using generated synthetic GeoTIFFs
- `research_protocol.md`, `architecture.md`, `literature_notes.md` — research design and assumptions
- `CLAUDE.md` — instructions for coding agents

## Scientific guardrails
- A synthetic fixture validates code, not real-world model accuracy.
- A mapped class change is not automatically a confirmed environmental change.
- Geographic coordinates do not have a constant ground pixel area; use geodesic areas for geographic rasters.
- No-data pixels are excluded. Zero valid area means a proportion is undefined.
- Language models must not invent measurements. Numerical claims should come from deterministic tools.
- A GeoProof record provides provenance, not automatic proof of truth.
- Novelty and dataset/model licences remain under review; see `literature_notes.md`.

## Planned next steps
1. Complete the synthetic GeoTIFF vertical slice and tests.
2. Add a controlled land-cover measurement workflow and documented public dataset only after licence review.
3. Implement a fair image-only versus evidence-grounded evaluation.
4. Consider pretrained model integration only after verifying requirements and compute feasibility.

See [MILESTONES.md](MILESTONES.md) and [acceptance_criteria.md](acceptance_criteria.md).
