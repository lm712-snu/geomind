import numpy as np
import pytest
import rasterio

from geomind.analysis import AnalysisError, class_area, row_pixel_areas_m2
from geomind.raster import RasterValidationError, inspect_raster, validate_aligned_pair


def test_inspect_metadata(synthetic_raster):
    info = inspect_raster(synthetic_raster)
    assert (info.width, info.height, info.count) == (3, 2, 1)
    assert info.crs == "EPSG:32643"
    assert info.nodata == 255


def test_missing_crs_is_rejected(missing_crs_raster):
    with pytest.raises(RasterValidationError, match="no CRS"):
        inspect_raster(missing_crs_raster)


def test_area_excludes_nodata_and_uses_valid_area(synthetic_raster):
    result = class_area(synthetic_raster, class_value=1)
    assert result["class_area_m2"] == pytest.approx(300.0)
    assert result["valid_area_m2"] == pytest.approx(500.0)
    assert result["class_proportion"] == pytest.approx(0.6)
    assert result["valid_pixels"] == 5
    assert result["status"] == "ok"


def test_zero_valid_pixels_proportion_is_undefined(tmp_path):
    path = tmp_path / "all_nodata.tif"
    with rasterio.open(
        path, "w", driver="GTiff", width=2, height=2, count=1, dtype="uint8",
        crs="EPSG:32643", transform=rasterio.transform.from_origin(0, 20, 10, 10),
        nodata=255,
    ) as dst:
        dst.write(np.full((2, 2), 255, dtype=np.uint8), 1)
    result = class_area(path, class_value=1)
    assert result["status"] == "no_valid_data"
    assert result["valid_area_m2"] == 0
    assert result["class_proportion"] is None


def test_geographic_pixel_area_varies_by_latitude(tmp_path):
    path = tmp_path / "latitudes.tif"
    with rasterio.open(
        path, "w", driver="GTiff", width=1, height=2, count=1, dtype="uint8",
        crs="EPSG:4326", transform=rasterio.transform.from_origin(0, 60, 1, 30),
        nodata=255,
    ) as dst:
        dst.write(np.ones((2, 1), dtype=np.uint8), 1)
    areas = row_pixel_areas_m2(path)
    assert areas[0] > 0 and areas[1] > 0
    assert areas[0] != pytest.approx(areas[1], rel=0.01)


def test_alignment_rejects_different_transform(synthetic_raster, tmp_path):
    other = tmp_path / "shifted.tif"
    with rasterio.open(
        other, "w", driver="GTiff", width=3, height=2, count=1, dtype="uint8",
        crs="EPSG:32643", transform=rasterio.transform.from_origin(500010, 3000000, 10, 10),
    ) as dst:
        dst.write(np.ones((2, 3), dtype=np.uint8), 1)
    with pytest.raises(RasterValidationError, match="transform mismatch"):
        validate_aligned_pair(synthetic_raster, other)


def test_rotated_geographic_grid_is_rejected(tmp_path):
    path = tmp_path / "rotated.tif"
    transform = rasterio.Affine(1, 0.1, 0, 0.1, -1, 10)
    with rasterio.open(path, "w", driver="GTiff", width=2, height=2, count=1,
                       dtype="uint8", crs="EPSG:4326", transform=transform) as dst:
        dst.write(np.ones((2, 2), dtype=np.uint8), 1)
    with pytest.raises(AnalysisError, match="Rotated geographic"):
        row_pixel_areas_m2(path)
