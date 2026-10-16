# CLAUDE.md — GeoMind project instructions

GeoMind: *From Satellite Imagery to Verifiable Geospatial Intelligence.*
Signature capability: **GeoProof**, an evidence ledger that makes geospatial AI answers traceable, measurable and reproducible.
Dual purpose: undergraduate mathematics research thesis + credible product prototype.

Research question: does grounding vision-language model responses in explicit GIS measurements and geospatial provenance improve factual accuracy and spatial consistency compared with image-only responses to questions about satellite imagery?

## Non-negotiable rules
1. **Inspect before building.** Read the repo and environment first. Never overwrite existing work blindly.
2. **Smallest complete slice.** Implement, run, test, then continue. No large unverified code dumps.
3. **Never fabricate.** No invented datasets, models, APIs, test results, metrics or maps. If something was not run, say it was not run. Show real test output.
4. **Numbers come from deterministic code**, never from a language model. LLMs may only plan/phrase, behind the same typed schemas.
5. **Abstain over guess.** Missing or invalid evidence → ask for clarification or abstain.
6. **Honest labels.** A visual heuristic is never called a trained model. Mapped-class change is never called confirmed real-world change. Confidence is never called calibrated unless calibration was evaluated. Cosine similarity is similarity, not correctness. An LLM's answer is never unquestioned ground truth.
7. **Provenance is not proof.** A GeoProof record documents how an answer was produced; the verifier independently recomputes the claim from the record.
8. **Safety.** Never execute generated code or shell commands. Tools are an explicit allowlist with validated arguments and output schemas. Secrets only via environment variables; keep `.env.example` credential-free.
9. **Licences first.** Check dataset licence, API terms, compute needs and commercial-use limits before integrating any data or model; record them in a dataset/model card.
10. **Do not suppress errors** to make a demo look successful.

## Environment constraints
- Target machine: 8 GB RAM, Intel i3, limited SSD. CPU-first; small samples; lazy/windowed raster reads. Colab/cloud GPU is optional and isolated behind adapters.
- Free/open-source tools and public data preferred. Core pipeline must work with **no paid API** (deterministic local mode).

## Stack (candidates; pin only after checking the local machine)
Python, rasterio, geopandas, shapely, pyproj, numpy, pydantic v2, Streamlit, folium, pytest, YAML/JSON. Keep dependencies lean.

## Layout
`src/geomind/{raster,analysis,proof,chat,eval}`, `app/`, `tests/`, `docs/`. See `docs/architecture.md`.

## Commands (planned — not yet implemented; update when real)
- Setup: `python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`
- Tests: `pytest -q`
- App: `streamlit run app/main.py`

## Working method (per phase)
Phases: 1 inspect → 2 architecture/protocol → 3 tested vertical slice → 4 workflow + baseline-vs-grounded eval → 5 pretrained model (only if it fits compute) → 6 polish.
At the end of every phase: list files created/changed; run tests and show actual results; give run instructions; state working / incomplete / blocked; update `MILESTONES.md`. Explain trade-offs before any major architectural decision.

## Maths conventions (defend these in the thesis)
See `docs/architecture.md` §Maths and `docs/research_protocol.md`. Area uses equal-area/geodesic pixel areas, never raw lon/lat pixel counts. Proportions use valid area only. Percentage-point change ≠ relative percentage change.
