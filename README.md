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


## Real-data and research pipeline (implementation in progress)

### Sentinel-2 catalog search
The optional STAC catalog client queries public Sentinel-2 L2A metadata through the
Element 84 Earth Search API. It returns item IDs, acquisition timestamps, cloud-cover
metadata, footprints, and available asset URLs. Catalog metadata alone does not
prove that a scene is cloud-free or suitable for analysis.

Install:
```bash
pip install -e ".[catalog]"
```

Example:
```python
from geomind.catalog import search_sentinel2
items = search_sentinel2(
    (77.20, 28.40, 77.55, 28.65), "2024-01-01", "2024-03-31",
    max_cloud_cover=20, limit=10,
)
for item in items:
    print(item["id"], item["datetime"], item["cloud_cover_percent"])
```

### NDVI analysis
`geomind.remote_sensing.calculate_ndvi(red_path, nir_path)` computes NDVI from
red and near-infrared raster bands, checks CRS/nodata, aligns the NIR raster to the
red grid when necessary, reports valid-pixel coverage, and can write an NDVI GeoTIFF.
Reflectance scaling must be appropriate for the downloaded asset. Its NDVI >= 0.3
vegetation-candidate rule is explicitly a heuristic, not ground truth. Date-to-date
comparisons require compatible scenes, masks, grids and acquisition conditions.

### Optional vision-language model
Install `pip install -e ".[vlm]"`, set `OPENAI_API_KEY` as an environment variable,
and optionally set `GEOMIND_VLM_MODEL`. The API key must never be committed. Call
`geomind.vlm.answer_image_question(...)` with an image preview and question. For a
controlled comparison, use the same model and settings for the image-only condition
(`evidence=None`) and the grounded condition (provide the computed evidence object).
A model response is not ground truth; numeric claims must be checked against tools.

### Evaluation helpers
`geomind.evaluation` includes exact-match accuracy, numeric MAE/RMSE/bias, paired
binary correctness summaries and unsupported-claim rate. These are scoring helpers,
not a completed benchmark. Research claims require a frozen test set, independent
reference answers, documented prompts/model versions, and appropriate uncertainty
intervals and paired statistical tests.

### Current limits
- The public website is a static explorer; it does not itself run the Python analysis
  backend. The backend is run locally or hosted separately.
- The STAC client searches for scenes; automatic download, cloud masking, scene
  compositing and full end-to-end date comparison still require integration.
- NDVI is implemented as a spectral indicator, not a validated vegetation map.
- VLM inference requires a compatible API key and can incur usage charges.
- No experimental performance claims should be made until the benchmark has been run.


## Website + Python API deployment

GitHub Pages serves the static globe only. The FastAPI service runs separately and
provides health checks, Sentinel-2 catalog search, NDVI raster processing, and an
optional hosted VLM endpoint.

### Deploy the API on Render

1. Open [Render](https://render.com/) and connect the GitHub repository
   `lm712-snu/geomind`.
2. Choose **New → Blueprint** and select this repository. Render reads `render.yaml`
   and proposes a `geomind-api` web service.
3. Review the service settings and deploy. The free service may sleep when idle.
4. Copy the deployed service URL (for example, `https://geomind-api.onrender.com`).
5. Open the GitHub Pages site and paste that URL into **Connect analysis backend**.
   Click **Test connection**; the expected health response is JSON with
   `"status": "ok"`.
6. Try **Search real satellite scenes**. The site sends the query to the API, which
   searches the public Element 84 Earth Search STAC catalog.
7. To run NDVI, select red and NIR GeoTIFFs from compatible acquisitions and use
   **Calculate NDVI**. The API accepts files up to 80 MB each.

### Run locally

```bash
python -m pip install -e ".[api,catalog,vlm]"
uvicorn backend.main:app --reload --port 8000
```

Open `http://127.0.0.1:8000/docs` for interactive API documentation and use
`http://127.0.0.1:8000` as the website API URL during local development. The API
allows the published GitHub Pages origin and localhost by default. Set
`GEOMIND_CORS_ORIGINS` to a comma-separated allowlist if needed.

### Optional VLM endpoint

The `/api/vlm/ask` endpoint requires a server-side `OPENAI_API_KEY`. Set it in the
Render service environment settings (never in website JavaScript or Git). An API key
is not required for health checks, catalog search or NDVI analysis. Requests to the
VLM may incur provider charges.

### API routes

- `GET /health` — service health
- `POST /api/catalog/sentinel-2` — search dated Sentinel-2 L2A metadata for a WGS84 bounding box
- `POST /api/analysis/ndvi` — calculate NDVI from uploaded red/NIR GeoTIFF bands
- `POST /api/vlm/ask` — optional image question-answering with supplied evidence
- `GET /docs` — interactive API documentation

**Important limits:** scene discovery does not download full scenes, cloud-mask them,
or prove pixel quality. NDVI is a spectral indicator and its candidate threshold is a
heuristic. The current API does not yet automatically create a complete GeoProof
record for every uploaded NDVI job or perform the complete two-date pipeline. Those
are subsequent integration milestones. Do not upload private or sensitive imagery
to a public demo service.
