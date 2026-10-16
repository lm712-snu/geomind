# Acceptance criteria

A criterion passes only when the test exists, was run, and its real output was shown.

## Slice 1 (Phase 3) — synthetic GeoTIFF, labelled synthetic everywhere
| ID | Criterion |
|----|-----------|
| AT-01 | A synthetic GeoTIFF loads; CRS, transform, nodata, dtype and dimensions match the generator's known values. |
| AT-02 | Missing CRS raises a typed, human-readable error. |
| AT-03 | Nodata is masked; valid-pixel count equals the analytically known count. |
| AT-04 | Zero valid pixels -> proportion `undefined` with explicit status; no divide-by-zero. |
| AT-05 | Projected CRS: A_k exact. Geographic CRS: A_k agrees with an independent pyproj-`Geod` computation within a stated tolerance at two latitudes. |
| AT-06 | Alignment check rejects mismatched CRS, transform or shape in a two-date pair. |
| AT-07 | Corrupt or non-GeoTIFF input yields a clean error, no crash. |
| AT-08 | GeoProof record validates against its schema, round-trips through JSON, and the verifier's recomputation from recorded operations/parameters reproduces the answer value. A tampered value yields `failed`. |
| AT-09 | Streamlit `AppTest` smoke test renders the result and evidence view without exceptions. |

## Phase gates
- **Phase 4:** evaluation script is repeatable (fixed seeds, recorded versions) and emits machine-readable results; baseline and grounded systems see identical items; sample size, CIs, effect sizes and failure cases are reported even if the result is null or negative.
- **Phase 5:** a pretrained model is integrated only if model, weights, input requirements, licence and execution path are verified and inference fits the compute budget; otherwise documented as blocked.
- **Phase 6:** fresh-clone setup works from the README; all tests pass; no secrets or large artefacts committed.
