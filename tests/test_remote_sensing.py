from __future__ import annotations

import numpy as np
import rasterio
import pytest
from rasterio.transform import from_origin

from geomind.remote_sensing import calculate_ndvi, compare_ndvi


def _write(path, arr, *, transform=None, crs="EPSG:32643", nodata=0):
    arr = np.asarray(arr, dtype=np.uint16)
    with rasterio.open(
        path, "w", driver="GTiff", width=arr.shape[1], height=arr.shape[0],
        count=1, dtype=arr.dtype, crs=crs,
        transform=transform or from_origin(500000, 3000000, 10, 10), nodata=nodata,
    ) as ds:
        ds.write(arr, 1)


def test_ndvi_known_values_and_output(tmp_path):
    red = tmp_path / "red.tif"
    nir = tmp_path / "nir.tif"
    output = tmp_path / "ndvi.tif"
    _write(red, [[100, 100], [100, 100]])
    _write(nir, [[300, 100], [500, 300]])
    result = calculate_ndvi(red, nir, output_path=output)
    assert result["index"] == "NDVI"
    assert result["valid_pixels"] == 4
    assert result["mean_ndvi"] == pytest.approx(0.5)
    assert result["vegetation_candidate_fraction_of_valid"] == pytest.approx(0.75)
    assert output.exists()
    with rasterio.open(output) as ds:
        assert ds.count == 1
        assert ds.read(1)[0, 0] == pytest.approx(0.5)


def test_ndvi_comparison_reports_percentage_points():
    before = {"mean_ndvi": 0.4, "vegetation_candidate_fraction_of_valid": 0.25}
    after = {"mean_ndvi": 0.5, "vegetation_candidate_fraction_of_valid": 0.50}
    result = compare_ndvi(before, after)
    assert result["mean_ndvi_delta"] == pytest.approx(0.1)
    assert result["fraction_delta_percentage_points"] == pytest.approx(25.0)
