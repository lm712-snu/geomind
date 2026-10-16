# Phase 3 implementation status

This repository change introduces the first vertical-slice implementation. It has not been run on the user's computer. Acceptance criteria must be marked complete only after the commands have been run in a real environment and their output reviewed.

## Implemented in code
- GeoTIFF metadata validation and alignment checks.
- Deterministic class area and valid-area proportion calculation.
- Projected pixel area converted using CRS axis unit factors; geographic pixel area computed geodesically by row for north-up grids.
- Pydantic GeoProof record and verifier that recomputes recorded measurements from row-level evidence.
- Synthetic fixtures and tests for core cases.
- Streamlit interface for synthetic raster analysis and proof inspection.

## Not yet implemented
- Natural-language tool planner / LLM integration.
- Real satellite data workflow and independently verified labels.
- Baseline-versus-grounded model evaluation.
- Real model inference, calibration study, or claims of improved accuracy.
- Production-grade map overlays and multi-scene comparison.

## Validation requirement
Run `pip install -e ".[dev]"` and `pytest -q`. If geospatial dependencies fail to install, record the exact OS/Python/error rather than silently substituting a different calculation.
