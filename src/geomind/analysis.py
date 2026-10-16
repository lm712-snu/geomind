"""Deterministic raster measurements. All returned areas are square metres."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio
from pyproj import CRS

from geomind.raster import RasterValidationError, read_valid_band


class AnalysisError(ValueError):
    """Raised when a measurement is undefined or its assumptions are not met."""


def row_pixel_areas_m2(path: str | Path) -> np.ndarray:
    """Return geodesic pixel area by row for geographic rasters, or constant area for projected."""
    with rasterio.open(path) as ds:
        if ds.crs is None:
            raise RasterValidationError("Cannot calculate area: raster has no CRS.")
        crs = CRS.from_user_input(ds.crs)
        t = ds.transform
        if crs.is_projected:
            if len(crs.axis_info) < 2:
                raise AnalysisError("Projected CRS lacks horizontal axis unit metadata.")
            fx = crs.axis_info[0].unit_conversion_factor
            fy = crs.axis_info[1].unit_conversion_factor
            area = abs(t.a * t.e - t.b * t.d) * fx * fy
            if not np.isfinite(area) or area <= 0:
                raise AnalysisError("Pixel area is not positive and finite.")
            return np.full(ds.height, area, dtype=np.float64)
        if crs.is_geographic:
            if not np.isclose(t.b, 0) or not np.isclose(t.d, 0):
                raise AnalysisError("Rotated geographic rasters are unsupported for row-wise area.")
            geod = crs.get_geod()
            areas = []
            for row in range(ds.height):
                left, top = t * (0, row)
                right, _ = t * (1, row)
                _, bottom = t * (0, row + 1)
                area, _ = geod.polygon_area_perimeter(
                    [left, right, right, left], [top, top, bottom, bottom]
                )
                areas.append(abs(area))
            result = np.asarray(areas, dtype=np.float64)
            if not np.all(np.isfinite(result)) or np.any(result <= 0):
                raise AnalysisError("Could not calculate positive geodesic pixel areas.")
            return result
        raise AnalysisError("Unsupported CRS type; use a projected or geographic CRS.")


def class_area(path: str | Path, class_value: int | float, band: int = 1) -> dict:
    """Calculate class area, valid area, and per-row evidence for a single-band raster."""
    data, valid, info = read_valid_band(path, band=band)
    row_areas = row_pixel_areas_m2(path)
    class_counts = [int(np.count_nonzero(valid[i] & (data[i] == class_value))) for i in range(data.shape[0])]
    valid_counts = [int(np.count_nonzero(valid[i])) for i in range(data.shape[0])]
    area = float(sum(n * a for n, a in zip(class_counts, row_areas, strict=True)))
    valid_area = float(sum(n * a for n, a in zip(valid_counts, row_areas, strict=True)))
    proportion = area / valid_area if valid_area > 0 else None
    return {
        "class_value": float(class_value), "class_area_m2": area,
        "valid_area_m2": valid_area, "class_proportion": proportion,
        "valid_pixels": int(valid.sum()), "total_pixels": int(data.size),
        "status": "ok" if valid_area > 0 else "no_valid_data", "crs": info.crs,
        "row_evidence": [
            {"row": i, "class_pixels": class_counts[i], "valid_pixels": valid_counts[i],
             "pixel_area_m2": float(row_areas[i])}
            for i in range(data.shape[0])
        ],
    }


def change_summary(before: dict, after: dict) -> dict:
    """Summarise class-area change; caller must ensure common valid coverage and comparability."""
    if before.get("status") != "ok" or after.get("status") != "ok":
        raise AnalysisError("Change is undefined when either observation has no valid area.")
    a0, a1 = float(before["class_area_m2"]), float(after["class_area_m2"])
    p0, p1 = before["class_proportion"], after["class_proportion"]
    return {
        "area_before_m2": a0, "area_after_m2": a1, "delta_area_m2": a1 - a0,
        "proportion_change_percentage_points": (p1 - p0) * 100,
        "relative_area_change_percent": ((a1 - a0) / a0 * 100) if a0 != 0 else None,
        "interpretation_limit": "Mapped-class change is not, by itself, confirmed real-world change.",
    }
