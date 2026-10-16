from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin


@pytest.fixture
def synthetic_raster(tmp_path: Path) -> Path:
    path = tmp_path / "known_classes.tif"
    data = np.array([[1, 1, 2], [1, 255, 2]], dtype=np.uint8)
    with rasterio.open(
        path, "w", driver="GTiff", width=3, height=2, count=1, dtype="uint8",
        crs="EPSG:32643", transform=from_origin(500000, 3000000, 10, 10), nodata=255,
    ) as dst:
        dst.write(data, 1)
    return path


@pytest.fixture
def missing_crs_raster(tmp_path: Path) -> Path:
    path = tmp_path / "no_crs.tif"
    data = np.ones((2, 2), dtype=np.uint8)
    with rasterio.open(
        path, "w", driver="GTiff", width=2, height=2, count=1, dtype="uint8",
        transform=from_origin(0, 20, 10, 10),
    ) as dst:
        dst.write(data, 1)
    return path
