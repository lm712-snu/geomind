# Research protocol — Mathematics of Computer Vision-Language Models applied to satellite imagery

**Status:** draft protocol. Freeze the dataset, prompts, thresholds, test split and model settings before evaluating the held-out set.

## Thesis alignment

GeoMind is the applied case study for the undergraduate thesis **Mathematics of Computer Vision Language Models**. The companion [CVLM thesis project](https://github.com/lm712-snu/cvlm-thesis) is responsible for explicitly teaching and demonstrating the mathematics of convolution, patch embeddings, attention, cross-modal alignment and language-generation scores. GeoMind asks a narrower empirical question about the reliability of VLM answers when grounded in geospatial measurements.

This protocol does not assume that the current website runs a CNN or transformer locally. Model inference is an optional research component; the raster/GIS pipeline and GeoProof verifier remain deterministic.

## Research question and hypotheses

**RQ:** Does grounding a VLM response in explicit GIS measurements and geospatial provenance improve factual correctness and spatial consistency over image-only responses?

- **H1 (primary):** on answerable items, per-item correctness is higher for the evidence-grounded condition than the image-only baseline.
- **H2 (secondary):** the grounded condition has a lower unsupported-claim rate and abstains more appropriately on unanswerable items.
- Null or negative results must be reported as such.

## Systems compared

- **S0 — image-only:** a VLM sees the same image and question, without a GeoProof evidence block.
- **S1 — evidence-grounded:** the same VLM, weights, prompt framework and generation settings receive the verified GeoProof evidence block (measurements, metadata, coverage and limitations).
- **S2 — deterministic tool output:** a templated output from GIS calculations, used to characterize what the tool layer can report; not the primary VLM comparison.

Keeping the VLM and settings fixed between S0 and S1 isolates the effect of grounding. Record model name/version, prompts, decoding settings, package versions, data hashes and all costs. If no model can be used within the available budget, report the implementation as not yet evaluated rather than substituting fabricated results.

## Mathematical path being studied

The project should explain these operations in the thesis companion and connect each one to a concrete GeoMind example:

1. Image/raster representation: (X\in\mathbb{R}^{H\times W\times C}), with spatial resolution, bands, CRS and nodata treated explicitly.
2. Convolution: (Y_{i,j,k}=\sum_{u,v,c}K_{u,v,c,k}X_{i+u,j+v,c}), with stride/padding conventions documented.
3. Patch representation and projection: (z_i=x_iW_E+b_E), with positional information described where applicable.
4. Attention: (\operatorname{softmax}(QK^\top/\sqrt{d_k})V).
5. Cross-modal similarity: (s=z_I^\top z_T) for normalized embeddings. Similarity is not evidence of truth.
6. Evidence grounding: deterministic area, proportion, coverage and metadata are serialized with their units and assumptions; the verifier recomputes what can be checked.

These equations explain the model family and analysis pipeline conceptually. Do not claim the current GeoMind website computes these model operations unless a tested implementation is added.

## Circularity guard

Reference answers must be independent of the measurement path used by S1: for example, human-verified labels/masks from a documented dataset or manual verification. Never use an LLM answer as ground truth or score S1 solely against the same raster calculation it receives. If independent reference data are unavailable for an item type, report internal consistency only or exclude that item type from accuracy claims.

## Items and question types

Use a fixed set of numeric (area, proportion, change), categorical (dominant class), spatial relation (contains/overlaps/direction) and unanswerable questions (missing metadata, invalid mask, unsupported request). Freeze templates, item counts and scoring rules before test evaluation. Report tool coverage because the grounded system can only answer questions its tools support.

## Geographic split

Hold out entire regions, not randomly selected neighbouring tiles. Tune prompts, thresholds and numeric tolerances on development data only. Evaluate the test split once. Document possible leakage from overlapping scenes, shared imagery, seasonality and related labels.

## Outcomes

- Primary: per-item correctness against independent reference answers.
- Numeric: MAE, RMSE and bias with units; tolerance-based correctness using thresholds fixed in advance.
- Spatial: relation accuracy and, where independent masks exist, IoU/Dice.
- Grounding: unsupported-claim rate, GeoProof verification rate and evidence coverage.
- Abstention: precision/recall on unanswerable questions.
- Calibration: Brier score/ECE only if meaningful confidence values and enough samples exist; otherwise mark not evaluated.

## Statistics

- Binary paired outcomes: exact McNemar test, discordant-pair counts, and paired-bootstrap 95% confidence interval for accuracy difference (fixed seed; at least 10,000 resamples if feasible).
- Numeric paired errors: Wilcoxon signed-rank test and median paired error difference with confidence interval.
- Cluster samples by scene/region where observations are not independent.
- Use one primary hypothesis; apply Holm correction to secondary tests.
- Report effect sizes and confidence intervals, not p-values alone. Small sample sizes and low statistical power must be stated explicitly.

## Reproducibility

Keep the question set, references, dataset versions/licences, prompts, model settings, seeds, input hashes, code versions and scoring outputs under version control where licensing permits. Store results in a documented JSON/CSV schema and provide a single repeatable evaluation command.

## Threats to validity

Classification error can propagate into measurements; seasonal and atmospheric conditions can undermine temporal comparisons; cloud/nodata masks can bias coverage; resolution mismatch can alter apparent objects; templates can bias answers; a small sample gives wide intervals; tool-coverage bias can favour S1; shared model outputs are dependent; and prompt sensitivity may affect outcomes.

## Data and model sources

Candidates are not approved until licences and terms are verified. For each dataset, record source, version, licence, citation, dates, CRS, spatial resolution, cloud-mask availability and any usage restrictions. For each model, record licence, inference requirements, version and cost.