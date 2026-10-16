# GeoMind
**A geospatial research testbed for the Mathematics of Computer Vision-Language Models**

GeoMind applies the mathematics of computer vision and vision-language models (CVLMs) to satellite imagery. It is the applied research companion to [Mathematics of Computer Vision Language Models](https://github.com/lm712-snu/cvlm-thesis): that thesis project explains the mathematical operations interactively, while GeoMind investigates what happens when image understanding is grounded in measurable, geographically referenced evidence.

> **Research status:** early scaffold. The current website visualizes Earth imagery and measures a user-drawn geographic boundary. The Python research code validates raster data, computes deterministic measurements, and builds GeoProof records. These components do not yet constitute a completed end-to-end pretrained CVLM experiment. No real-world model performance or research result is claimed.

## Thesis connection

**Thesis question:** How do the mathematical representations and operations in a vision-language model support reliable interpretation of satellite imagery, and does adding verified geospatial evidence improve the factual and spatial consistency of its answers?

GeoMind links four layers:

1. **Image mathematics** — pixels, channels, spatial resolution, raster grids, convolutional filters and feature maps.
2. **Vision representations** — patches, embeddings, positional information and image-text similarity. Similarity is a relevance signal, not proof that a claim is true.
3. **Language and multimodal reasoning** — attention, visual/text alignment, generated claims, and limits of what the image supports.
4. **Evidence-grounded evaluation** — deterministic GIS measurements, metadata, provenance, verification, uncertainty and abstention.

The interactive mathematical explanations live in the companion [CVLM thesis repository](https://github.com/lm712-snu/cvlm-thesis). GeoMind is the domain-specific research environment used to connect those ideas to remote sensing.

## Research question and comparison

Primary question: **Does grounding a VLM's response in explicit GIS measurements and provenance improve correctness compared with giving the same VLM the image and question alone?**

- **S0 — image-only:** same image, question, model and generation settings; no GeoProof evidence.
- **S1 — evidence-grounded:** same model and settings, with a verified evidence record containing measurements, acquisition metadata, valid coverage and limitations.
- **S2 — deterministic tool output:** a reference for what the GIS calculation can report without language generation; not treated as a competing VLM.

Evaluate per-item correctness, numeric MAE/RMSE, spatial-relation accuracy, unsupported-claim rate, evidence-verification rate and appropriate abstention. Use independent reference labels, geographic holdouts and paired statistical analysis. Report null or negative findings honestly.

## Current implementation

- Validate GeoTIFF CRS, transform, dimensions, nodata and grid alignment.
- Calculate class area and class proportion using valid pixels.
- Handle projected and geographic pixel-area calculations with explicit assumptions.
- Create a structured GeoProof record and independently recompute recorded measurements.
- Calculate NDVI from compatible red and near-infrared rasters.
- Search Sentinel-2 catalog metadata through STAC.
- Provide a minimal Streamlit interface and a static Earth explorer.
- Test important edge cases using synthetic rasters with known expected values.

The public static website is an imagery-and-geometry explorer, not a pixel classifier. A polygon drawn by the user is not evidence that the enclosed area is vegetation, a building, a flood or a land-cover class.

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

The Streamlit app includes a small synthetic raster demonstration. **Synthetic data validates software behaviour; it is not a satellite observation or a model-accuracy result.**

Optional integrations:

```bash
pip install -e ".[catalog]"  # STAC catalog search
pip install -e ".[vlm]"      # hosted VLM adapter
```

A VLM adapter may require an API key and incur costs. Never commit secrets. Heavy model inference is optional; core GIS calculations and tests should remain CPU-feasible.

## Mathematical foundations to make explicit

- **Convolution:** for image tensor (X) and kernel (K), feature responses are weighted local sums (with channel and padding/stride conventions stated).
- **Patch embedding:** flatten each image patch and project it to a vector, e.g. (z_i = x_i W_E + b_E).
- **Attention:** (Q=XW_Q, K=XW_K, V=XW_V), and (mathrm{Attention}(Q,K,V)=\mathrm{softmax}(QK^\top/\sqrt{d_k})V).
- **Cross-modal alignment:** normalized visual and text embeddings can be compared by cosine similarity (s=z_I^\top z_T); this does not establish factual correctness.
- **Geospatial measurements:** area and proportions must account for CRS, pixel footprint, nodata and valid coverage.
- **Grounding:** each numeric or spatial claim should map to a reproducible tool result and a GeoProof entry; the verifier checks the record's arithmetic and provenance fields.

These equations are the conceptual bridge to the interactive calculations in the [CVLM thesis project](https://github.com/lm712-snu/cvlm-thesis). Do not imply that the current GeoMind website itself executes a CNN or transformer unless such an implementation is explicitly added and tested.

## Repository guide

- `src/geomind/raster.py` — raster metadata and alignment validation
- `src/geomind/analysis.py` — area/proportion calculations
- `src/geomind/remote_sensing.py` — NDVI and remote-sensing helpers
- `src/geomind/catalog.py` — Sentinel-2 STAC catalog search
- `src/geomind/proof.py` — GeoProof schema, builder and verifier
- `src/geomind/vlm.py` — optional hosted VLM adapter
- `src/geomind/evaluation.py` — scoring helpers, not a completed benchmark
- `app/main.py` — minimal Streamlit demonstration
- `docs/index.html` — static Earth imagery and boundary-measurement explorer
- `research_protocol.md`, `architecture.md`, `literature_notes.md` — research design

## Scientific guardrails

- A synthetic fixture validates code, not real-world model accuracy.
- A similarity score is not a truth score.
- A mapped class change is not automatically a confirmed environmental change.
- Geographic coordinates do not have constant ground pixel area; calculations must account for projection or geodesic area.
- No-data pixels are excluded; zero valid area makes a proportion undefined.
- Language models must not invent measurements. Numeric claims come from deterministic tools.
- GeoProof records provenance and arithmetic consistency; it does not automatically prove that the source data or interpretation is true.
- Reference labels must be independent of the method being evaluated to avoid circular scoring.
- Dataset and model licences, compute requirements, geographic splits and related work must be reviewed before experiments.
- No experimental performance claims should be made until a documented benchmark has been run.

## Roadmap

1. Verify the deterministic raster and GeoProof workflow in CI and locally.
2. Select one documented, licence-checked satellite dataset and one bounded research task.
3. Explain the relevant convolution/patch/embedding/attention mathematics in the CVLM companion lab.
4. Freeze a small, independently labelled, geographically held-out question set.
5. Compare image-only and evidence-grounded answers with the same VLM and settings.
6. Report paired metrics, failure cases, limitations and reproducibility artifacts.

See [MILESTONES.md](MILESTONES.md), [research_protocol.md](research_protocol.md), and [acceptance_criteria.md](acceptance_criteria.md).
