# Research protocol (draft v0.1 — to be frozen before any test-set evaluation)

## Question and hypotheses
RQ: does grounding VLM responses in explicit GIS measurements and provenance improve factual accuracy and spatial consistency versus image-only responses?
- H1 (primary): on answerable items, per-item correctness is higher for the grounded system than the image-only baseline.
- H2 (secondary): the grounded system has a lower unsupported-claim rate and abstains more appropriately on unanswerable items.
Null results are reported as such.

## Systems compared (same images, questions, reference answers, scoring)
- **S0 image-only:** a VLM sees the image(s) and the question only.
- **S1 grounded:** the *same* VLM (same weights/settings) additionally receives the GeoProof evidence block (computed measurements, metadata, limitations). Using the same model isolates the effect of grounding; changing models would confound it.
- **S2 deterministic reference (no LLM):** tools + templated answers. Shows the ceiling of the tool layer, not a competitor in the primary test.
Which VLM is used is decided in Phase 4/5 against the compute budget and recorded with version and settings.

## Circularity guard (critical)
Reference answers must come from a source **independent of the measurement path of S1**: e.g. human-verified labels/masks from a documented dataset, or manual verification. Never from an LLM's output, and never from the same classifier/raster computation S1 uses to answer. If an independent reference is unavailable for an item type, that item type is excluded or reported as "internal consistency only", not "accuracy".

## Items
Question types: numeric (area, proportion, change), categorical (dominant class), spatial relation (contains/overlaps/direction), and **unanswerable** (missing metadata, invalid mask, out-of-scope) where the correct behaviour is to ask or abstain. Templates and counts are fixed and documented before testing. Report **tool coverage** (share of items the tools can answer), since coverage favours S1.

## Splits
Geographic holdout: assign whole regions (not tiles) to dev vs test. Prompts, tolerances and thresholds are tuned on dev only; the test split is evaluated once. Report any leakage risks (overlapping scenes, shared source imagery).

## Outcomes
- **Primary:** per-item correctness. Categorical/spatial: exact match to reference. Numeric: correct if |ŷ − y| ≤ max(abs_tol, rel_tol·|y|), with tolerances fixed in advance.
- **Secondary:** numeric MAE and RMSE (with units); IoU where masks exist (edge cases per architecture doc); spatial-relation accuracy; unsupported-claim rate (a claim not entailed by the evidence record, via rule-based check plus a manual audit sample); evidence-validity rate (verifier status); abstention precision/recall on unanswerable items.

## Statistics (paired by item)
- Binary outcomes: exact McNemar test; effect = difference in accuracy with 95% CI from a paired bootstrap (fixed seed, ≥10,000 resamples), plus discordant-pair counts.
- Numeric errors: Wilcoxon signed-rank on paired absolute errors; effect = median paired difference with bootstrap CI and rank-biserial correlation.
- Items from the same scene/region are not independent: use a **cluster bootstrap** at scene/region level.
- One primary hypothesis; secondary tests reported with Holm correction. Always give CIs, not only p-values.
- Precision illustration (arithmetic): with n = 100 and accuracy near 0.5, a simple 95% interval half-width is about ±9.8 percentage points. Small samples give wide intervals; this will be stated, not hidden.
- Calibration (ECE/Brier/reliability) only if confidences exist and the sample supports it; otherwise "not evaluated". No output is called "calibrated" without that evaluation.

## Reproducibility
Fixed seeds; recorded package versions, input hashes and config; results written as JSON/CSV with a schema; one command reruns the evaluation.

## Threats to validity (to be extended)
Classification error propagating into measurements; temporal comparability and season; cloud cover/invalid pixels; resolution mismatch; template bias in questions; small N; tool-coverage bias; dependence between S0/S1 outputs when sharing a model (handled by pairing); prompt sensitivity.

## Data and model sources — UNVERIFIED candidates
No dataset below is confirmed usable yet. Before integration, record in a dataset card: licence/terms, commercial-use limits, size, CRS, dates, resolution, cloud mask availability, citation.
- Synthetic rasters (own generator): fully known truth; used for Slice 1.
- Public land-cover products and Sentinel-2 archives: candidates only; licences and versions to be verified.
- GEOBench-VLM: aggregates multiple source datasets; per-source licences to be verified (see `literature_notes.md`).
