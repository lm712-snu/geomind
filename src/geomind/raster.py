"""GeoTIFF inspection and validation helpers."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import rasterio
from rasterio.errors import RasterioError


class RasterValidationError(ValueError):
    """Raised when a raster cannot be safely used for analysis."""


@dataclass(frozen=True)
class RasterInfo:
    path: str
    width: int
    height: int
    count: int
    dtype: str
    crs: str
    bounds: tuple[float, float, float, float]
    nodata: float | int | None
    transform: tuple[float, ...]


def inspect_raster(path: str | Path) -> RasterInfo:
    """Open a raster and return validated, human-readable metadata."""
    path = Path(path)
    if not path.is_file():
        raise RasterValidationError(f"Raster file does not exist: {path}")
    try:
        with rasterio.open(path) as ds:
            if ds.crs is None:
                raise RasterValidationError("Raster has no CRS; define its coordinate system first.")
            if ds.width < 1 or ds.height < 1 or ds.count < 1:
                raise RasterValidationError("Raster has invalid dimensions or no bands.")
            if ds.transform.is_identity:
                raise RasterValidationError("Raster has an identity transform; georeferencing is missing.")
            return RasterInfo(
                path=str(path), width=ds.width, height=ds.height, count=ds.count,
                dtype=ds.dtypes[0], crs=ds.crs.to_string(),
                bounds=(ds.bounds.left, ds.bounds.bottom, ds.bounds.right, ds.bounds.top),
                nodata=ds.nodata, transform=tuple(ds.transform),
            )
    except RasterValidationError:
        raise
    except (RasterioError, OSError, ValueError) as exc:
        raise RasterValidationError(f"Could not read a valid GeoTIFF: {exc}") from exc


def validate_aligned_pair(path_a: str | Path, path_b: str | Path) -> None:
    """Reject raster pairs whose grids differ; no implicit resampling is performed."""
    for path in (path_a, path_b):
        inspect_raster(path)
    with rasterio.open(path_a) as a, rasterio.open(path_b) as b:
        if a.crs != b.crs:
            raise RasterValidationError("Raster pair CRS mismatch.")
        if a.transform != b.transform:
            raise RasterValidationError("Raster pair transform mismatch.")
        if (a.width, a.height) != (b.width, b.height):
            raise RasterValidationError("Raster pair shape mismatch.")


def read_valid_band(path: str | Path, band: int = 1) -> tuple[np.ndarray, np.ndarray, RasterInfo]:
    """Read one band and its valid-data mask; intended for small MVP rasters."""
    info = inspect_raster(path)
    with rasterio.open(path) as ds:
        if band < 1 or band > ds.count:
            raise RasterValidationError(f"Band must be between 1 and {ds.count}.")
        data = ds.read(band)
        valid = ds.read_masks(band) > 0
        if np.issubdtype(data.dtype, np.floating):
            valid &= np.isfinite(data)
        return data, valid, info
