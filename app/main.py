"""Minimal GeoMind demo: synthetic raster -> GIS measurement -> GeoProof."""
from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import rasterio
import streamlit as st
from rasterio.transform import from_origin

from geomind.analysis import class_area
from geomind.proof import build_class_area_proof
from geomind.raster import inspect_raster


def make_synthetic_raster(path: str | Path) -> Path:
    """Create a clearly synthetic, known-value raster for safe demonstration."""
    path = Path(path)
    data = np.array([
        [1, 1, 1, 2, 2, 2],
        [1, 1, 2, 2, 2, 2],
        [1, 255, 2, 2, 1, 1],
        [2, 2, 2, 1, 1, 1],
    ], dtype=np.uint8)
    with rasterio.open(
        path, "w", driver="GTiff", width=data.shape[1], height=data.shape[0],
        count=1, dtype="uint8", crs="EPSG:32643",
        transform=from_origin(500000, 3000000, 10, 10), nodata=255,
    ) as dst:
        dst.write(data, 1)
    return path


st.set_page_config(page_title="GeoMind · GeoProof", page_icon="🌍", layout="wide")
st.title("GeoMind")
st.caption("From Satellite Imagery to Verifiable Geospatial Intelligence")
st.info("Demo mode: the input below is a synthetic software fixture, not satellite imagery.")
st.markdown("Ask a measurable question. GeoMind calculates the result with GIS code and shows the evidence record.")

with st.sidebar:
    st.header("Analysis setup")
    class_value = st.selectbox("Class value", options=[1, 2], index=0)
    st.caption("In this synthetic fixture, class values 1 and 2 are arbitrary labels.")
    run = st.button("Run analysis", type="primary", use_container_width=True)

if run or "geomind_last_result" not in st.session_state:
    with tempfile.TemporaryDirectory() as tmp:
        raster_path = make_synthetic_raster(Path(tmp) / "synthetic_classes.tif")
        info = inspect_raster(raster_path)
        result = class_area(raster_path, class_value=class_value)
        proof = build_class_area_proof(
            result, f"What area is covered by class {class_value}?",
            "generated-synthetic-fixture", data_kind="synthetic",
        )
        # Preserve only serialisable values, not the temporary file path.
        st.session_state["geomind_last_result"] = result
        st.session_state["geomind_last_info"] = info.__dict__
        st.session_state["geomind_last_proof"] = proof.model_dump(mode="json")

result = st.session_state["geomind_last_result"]
info = st.session_state["geomind_last_info"]
proof = st.session_state["geomind_last_proof"]

left, right = st.columns([1.1, 1])
with left:
    st.subheader("Raster preview")
    with tempfile.TemporaryDirectory() as tmp:
        path = make_synthetic_raster(Path(tmp) / "preview.tif")
        with rasterio.open(path) as ds:
            arr = ds.read(1).astype(float)
        arr[arr == 255] = np.nan
        st.image(arr, caption="Synthetic class labels (not a satellite image)", clamp=True, use_container_width=True)
    st.caption(f"Grid: {info['width']} × {info['height']} pixels · CRS: {info['crs']} · nodata: {info['nodata']}")
with right:
    st.subheader("Measured result")
    if result["status"] == "ok":
        st.metric("Class area", f"{result['class_area_m2']:,.0f} m²")
        st.metric("Share of valid area", f"{result['class_proportion'] * 100:.1f}%")
        st.metric("Valid pixels", f"{result['valid_pixels']} / {result['total_pixels']}")
    else:
        st.warning("No valid pixels: class proportion is undefined.")
    st.caption("Area is calculated from the declared projected CRS and affine pixel transform.")

st.subheader("GeoProof · evidence ledger")
status = proof["verification_status"]
st.write(f"Verification status: **{status.upper()}**")
st.write(proof["answer"])
with st.expander("Inspect full evidence record", expanded=True):
    st.json(proof)
st.warning("Verification recomputes the arithmetic from the recorded row evidence. It does not validate the source classification or prove that the raster represents the real world.")
