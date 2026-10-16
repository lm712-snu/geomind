"""Real-data vegetation analysis for aligned red/NIR satellite bands.

This module deliberately separates vegetation-index estimation from ground-truth
classification. NDVI is a spectral indicator, not a validated land-cover classifier.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import Resampling, reproject

from geomind.raster import RasterValidationError


class RemoteSensingError(ValueError):
    """Raised when satellite inputs cannot support a defensible analysis."""


def _read_band(path: str | Path):
    with rasterio.open(path) as ds:
        if ds.count < 1:
            raise RemoteSensingError(f"No raster band found in {path}")
        data = ds.read(1).astype(np.float32)
        valid = ds.read_masks(1) > 0
        if ds.nodata is not None:
            valid &= data != ds.nodata
        if ds.crs is None:
            raise RasterValidationError(f"Missing CRS in {path}")
        return data, valid, ds.profile.copy(), ds.transform, ds.crs


def calculate_ndvi(
    red_path: str | Path,
    nir_path: str | Path,
    *,
    output_path: str | Path | None = None,
    red_scale: float = 1.0,
    nir_scale: float = 1.0,
    min_valid_fraction: float = 0.5,
) -> dict:
    """Calculate NDVI from red and near-infrared rasters.

    Inputs must use compatible reflectance scaling. If grids differ, the NIR band
    is reprojected to the red grid with bilinear resampling. The function records
    the alignment decision and does not treat NDVI thresholds as ground truth.
    """
    if not 0 < min_valid_fraction <= 1:
        raise RemoteSensingError("min_valid_fraction must be in (0, 1].")
    if red_scale <= 0 or nir_scale <= 0:
        raise RemoteSensingError("Reflectance scale factors must be positive.")

    red, red_valid, red_profile, red_transform, red_crs = _read_band(red_path)
    nir, nir_valid, nir_profile, nir_transform, nir_crs = _read_band(nir_path)
    aligned = (
        red.shape == nir.shape
        and red_transform == nir_transform
        and red_crs == nir_crs
    )
    if not aligned:
        aligned_nir = np.full(red.shape, np.nan, dtype=np.float32)
        reproject(
            source=nir,
            destination=aligned_nir,
            src_transform=nir_transform,
            src_crs=nir_crs,
            dst_transform=red_transform,
            dst_crs=red_crs,
            resampling=Resampling.bilinear,
            src_nodata=np.nan,
            dst_nodata=np.nan,
        )
        aligned_mask = np.zeros(red.shape, dtype=np.uint8)
        reproject(
            source=nir_valid.astype(np.uint8),
            destination=aligned_mask,
            src_transform=nir_transform,
            src_crs=nir_crs,
            dst_transform=red_transform,
            dst_crs=red_crs,
            resampling=Resampling.nearest,
            src_nodata=0,
            dst_nodata=0,
        )
        nir, nir_valid = aligned_nir, aligned_mask.astype(bool)

    red = red * red_scale
    nir = nir * nir_scale
    valid = red_valid & nir_valid & np.isfinite(red) & np.isfinite(nir)
    denominator = nir + red
    valid &= np.abs(denominator) > 1e-8
    ndvi = np.full(red.shape, np.nan, dtype=np.float32)
    ndvi[valid] = (nir[valid] - red[valid]) / denominator[valid]
    valid &= np.isfinite(ndvi)
    ndvi[valid] = np.clip(ndvi[valid], -1.0, 1.0)
    valid_fraction = float(valid.mean()) if valid.size else 0.0
    if valid_fraction < min_valid_fraction:
        raise RemoteSensingError(
            f"Only {valid_fraction:.1%} valid pixels; required {min_valid_fraction:.1%}. "
            "Check nodata, band alignment, clouds and scale factors."
        )

    # A threshold is a transparent heuristic, not a universal vegetation truth.
    vegetation = valid & (ndvi >= 0.3)
    result = {
        "index": "NDVI",
        "formula": "(NIR - Red) / (NIR + Red)",
        "threshold_rule": "vegetation_candidate if NDVI >= 0.3",
        "threshold_is_universal_truth": False,
        "valid_pixels": int(valid.sum()),
        "total_pixels": int(valid.size),
        "valid_fraction": valid_fraction,
        "mean_ndvi": float(np.mean(ndvi[valid])),
        "median_ndvi": float(np.median(ndvi[valid])),
        "vegetation_candidate_pixels": int(vegetation.sum()),
        "vegetation_candidate_fraction_of_valid": float(vegetation.sum() / valid.sum()),
        "grid_aligned_without_resampling": aligned,
        "crs": str(red_crs),
        "transform": tuple(red_transform),
        "width": int(red.shape[1]),
        "height": int(red.shape[0]),
        "limitations": [
            "NDVI is a spectral indicator; NDVI >= 0.3 is a heuristic candidate rule, not ground truth.",
            "Cloud, shadow, snow, atmospheric correction and seasonal differences can affect results.",
            "Area change is interpretable only when dates, grid, valid coverage and methods are comparable.",
        ],
    }
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        profile = red_profile.copy()
        profile.update(driver="GTiff", count=1, dtype="float32", nodata=-9999.0,
                       compress="deflate", height=ndvi.shape[0], width=ndvi.shape[1],
                       transform=red_transform, crs=red_crs)
        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(np.where(valid, ndvi, -9999.0).astype(np.float32), 1)
            dst.set_band_description(1, "NDVI")
        result["ndvi_output_path"] = str(output_path)
    return result


def compare_ndvi(before: dict, after: dict) -> dict:
    """Compare two NDVI summaries while making comparability caveats explicit."""
    delta = float(after["mean_ndvi"] - before["mean_ndvi"])
    return {
        "mean_ndvi_before": float(before["mean_ndvi"]),
        "mean_ndvi_after": float(after["mean_ndvi"]),
        "mean_ndvi_delta": delta,
        "vegetation_candidate_fraction_before": float(before["vegetation_candidate_fraction_of_valid"]),
        "vegetation_candidate_fraction_after": float(after["vegetation_candidate_fraction_of_valid"]),
        "fraction_delta_percentage_points": 100.0 * (
            after["vegetation_candidate_fraction_of_valid"]
            - before["vegetation_candidate_fraction_of_valid"]
        ),
        "interpretation": (
            "Spectral-index summary difference only; not confirmed ecological change. "
            "Confirm comparable acquisition conditions and valid spatial coverage."
        ),
    }
