# GeoMind architecture (v0.1, Phase 2)

## Principles
1. Numbers come from deterministic code. Language models may plan and phrase only.
2. Every answer ships a GeoProof record; an independent verifier recomputes it.
3. Abstain rather than guess. 4. Local/CPU-first; heavy models are optional adapters.

## Packages
```
src/geomind/
  raster/    open GeoTIFF, validate CRS/transform/nodata/dtype, alignment checks, windowed reads
  analysis/  pure functions: class area, proportion, change, IoU, MAE/RMSE
  proof/     GeoProof schema (pydantic), builder, independent verifier
  chat/      question -> Plan (typed, allowlisted tools) -> validate -> execute  [Phase 3+]
  eval/      baseline-vs-grounded harness, stats, machine-readable results      [Phase 4]
app/         Streamlit UI: map + analysis workspace, chat panel, evidence drawer
tests/       pytest with synthetic fixtures
```

## Data flow for one question
`question -> planner -> Plan(tool, typed args) -> argument validation -> tool execution
-> ToolResult (schema-checked) -> GeoProof builder -> verifier -> answer renderer`
Each statement in the answer is tagged **observed** (metadata), **computed** (deterministic measurement),
**predicted** (model output) or **hypothesis**. Missing/invalid evidence -> clarification or abstention.

## GeoProof record (fields)
question, answer; dataset + asset id; acquisition date(s); spatial extent; CRS; valid-data coverage;
model name/version/settings (or `none`); operations + parameters; measurements with units and
intermediate values; links to map layers/outputs; uncertainty, assumptions, limitations;
`verification_status` in {verified, unverified, failed, not_applicable}; reproducibility info
(package versions, input hashes, config) and timestamps.
Limitation to state in the thesis: the verifier shares libraries with the pipeline, so independence is partial.
Mitigation: cross-check areas with a second formulation (see AT-05) and keep tolerances explicit.

## Decisions (defaults adopted unless you object)
| ID | Decision | Trade-off |
|----|----------|-----------|
| D1 | Streamlit + folium, reprojected PNG `ImageOverlay`; no tile server | Few dependencies, fits 8 GB. Only suits small/cropped rasters; a tile server scales better but adds a moving part. |
| D2 | Equal-area/geodesic pixel areas (below); never resample just to count | Exact and defensible; slightly more code than pixel counting. |
| D3 | Pydantic v2 for evidence records and tool schemas | Validation + JSON Schema export for one dependency; dataclasses are lighter but easier to get wrong. |
| D4 | `venv` + pip wheels, src layout, `pyproject.toml` | Light on disk vs conda. Depends on rasterio wheels working on your machine (wheel exists for Linux x86_64 CPython 3.12; not yet installed/tested; your Python version unknown). |
| D5 | Rule/template planner first; optional LLM planner behind the same `Plan` schema | Limited question coverage, but deterministic and testable; no paid API needed. |

## Maths
**Valid mask.** V = pixels not equal to nodata, not NaN, and (if present) inside the ROI. A_valid = sum over V of pixel area.

**Pixel area.**
- Projected CRS with affine transform (a, b, d, e): pixel area = |a·e − b·d| in CRS units². Use only if the CRS is equal-area or distortion is documented; otherwise reproject the *measurement* geometry, not the data.
- Geographic CRS (regular lat/lon grid): pixel area depends only on row. Compute a_i for row i as the geodesic area of that row's pixel polygon (pyproj `Geod` on the WGS84 ellipsoid).
  Sphere sanity check: a_i ≈ R²·Δλ·(sin φ_top − sin φ_bottom).
  Then A_k = sum over rows i of n_{k,i}·a_i, where n_{k,i} is the count of valid class-k pixels in row i. This costs O(rows) geodesic calls, not O(pixels).

**Class proportion.** p_k = A_k / A_valid. If A_valid = 0, p_k is *undefined* (status `no_valid_data`), never 0 and never an exception.

**Change.** ΔA = A_t2 − A_t1. Percentage-point change Δp_k = (p_k,t2 − p_k,t1)·100 pp. Relative change = ΔA / A_t1 · 100 %, undefined if A_t1 = 0. Compare dates on the **intersection** of both valid masks so cloud/nodata differences do not masquerade as change. Mapped-class change ≠ confirmed real-world change.

**IoU.** |P ∩ G| / |P ∪ G|. Both empty -> undefined (`both_empty`), excluded from means and reported separately. One empty, other not -> 0.

**Numeric error.** MAE = mean |ŷ − y|; RMSE = sqrt(mean (ŷ − y)²), with units. Paired comparison and statistics: see `research_protocol.md`.

## Out of scope for the MVP
Tile server, SAR/multispectral model training, live API ingestion, authentication, multi-user state.
