"""GeoMind HTTP API: catalog search, raster NDVI and evidence-grounded Q&A."""
from __future__ import annotations

import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from geomind.catalog import CatalogError, search_sentinel2
from geomind.remote_sensing import RemoteSensingError, calculate_ndvi, compare_ndvi

app = FastAPI(
    title="GeoMind API",
    version="0.1.0",
    description="Evidence-grounded geospatial analysis API. Outputs include limitations and provenance.",
)

allowed_origins = [
    item.strip()
    for item in os.getenv(
        "GEOMIND_CORS_ORIGINS",
        "https://lm712-snu.github.io,http://localhost:8000,http://127.0.0.1:8000",
    ).split(",")
    if item.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


class CatalogRequest(BaseModel):
    west: float = Field(ge=-180, le=180)
    south: float = Field(ge=-90, le=90)
    east: float = Field(ge=-180, le=180)
    north: float = Field(ge=-90, le=90)
    start_date: date
    end_date: date
    max_cloud_cover: float = Field(default=30, ge=0, le=100)
    limit: int = Field(default=10, ge=1, le=30)


class VLMRequest(BaseModel):
    image_data_url: str = Field(description="Base64 data URL for a PNG/JPEG/WEBP preview")
    question: str = Field(min_length=3, max_length=1500)
    evidence: dict[str, Any] | None = None
    model: str | None = None


@app.get("/")
def root():
    return {
        "service": "GeoMind API",
        "status": "ok",
        "docs": "/docs",
        "endpoints": ["/health", "/api/catalog/sentinel-2", "/api/analysis/ndvi", "/api/vlm/ask"],
        "limitations": [
            "Catalog search returns scene metadata and links; it does not download or cloud-mask scenes.",
            "NDVI endpoint accepts aligned or reprojectable red/NIR GeoTIFF bands.",
            "VLM endpoint requires OPENAI_API_KEY configured as a server environment variable.",
        ],
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "geomind-api", "version": app.version}


@app.post("/api/catalog/sentinel-2")
def sentinel_catalog(request: CatalogRequest):
    if request.start_date > request.end_date:
        raise HTTPException(status_code=422, detail="start_date must be on or before end_date")
    try:
        items = search_sentinel2(
            (request.west, request.south, request.east, request.north),
            request.start_date,
            request.end_date,
            max_cloud_cover=request.max_cloud_cover,
            limit=request.limit,
        )
        return {
            "provider": "Element 84 Earth Search STAC API",
            "collection": "sentinel-2-l2a",
            "query": request.model_dump(mode="json"),
            "count": len(items),
            "items": items,
            "note": "Scene metadata is not a cloud-free guarantee. Inspect band assets and masks before analysis.",
        }
    except CatalogError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/analysis/ndvi")
async def ndvi_analysis(
    red: UploadFile = File(...),
    nir: UploadFile = File(...),
    red_scale: float = Form(1.0, gt=0),
    nir_scale: float = Form(1.0, gt=0),
    min_valid_fraction: float = Form(0.5, gt=0, le=1),
):
    for file in (red, nir):
        if not file.filename or not file.filename.lower().endswith((".tif", ".tiff")):
            raise HTTPException(status_code=415, detail="Upload red and NIR GeoTIFF files (.tif/.tiff).")
    # Limit upload sizes to reduce memory/disk abuse on a small free service.
    max_bytes = 80 * 1024 * 1024
    with tempfile.TemporaryDirectory(prefix="geomind-") as tmp:
        paths = []
        for upload, name in ((red, "red.tif"), (nir, "nir.tif")):
            data = await upload.read(max_bytes + 1)
            if len(data) > max_bytes:
                raise HTTPException(status_code=413, detail="Each band must be 80 MB or smaller.")
            path = Path(tmp) / name
            path.write_bytes(data)
            paths.append(path)
        try:
            result = calculate_ndvi(
                paths[0], paths[1],
                red_scale=red_scale,
                nir_scale=nir_scale,
                min_valid_fraction=min_valid_fraction,
            )
        except (RemoteSensingError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"Could not read/align rasters: {exc}") from exc
        result["input_assets"] = {
            "red": {"filename": red.filename, "content_type": red.content_type},
            "nir": {"filename": nir.filename, "content_type": nir.content_type},
        }
        result["provenance"] = {
            "operation": "NDVI = (NIR - Red) / (NIR + Red)",
            "implementation": "geomind.remote_sensing.calculate_ndvi",
            "source_date": None,
            "source_ids": None,
            "note": "Provide and retain source IDs/acquisition dates in your study record; they cannot be inferred safely from filenames.",
        }
        return result


@app.post("/api/vlm/ask")
def vlm_ask(request: VLMRequest):
    try:
        import base64
        import re
        from geomind.vlm import build_grounding_prompt, VLMError
        from openai import OpenAI

        match = re.fullmatch(r"data:image/(png|jpeg|webp|gif);base64,([A-Za-z0-9+/=\s]+)", request.image_data_url)
        if not match:
            raise HTTPException(status_code=422, detail="image_data_url must be a supported image base64 data URL.")
        mime = "image/" + match.group(1)
        encoded = match.group(2).strip()
        if len(encoded) > 12 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Image preview is too large (maximum encoded size 12 MB).")
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise HTTPException(status_code=503, detail="VLM is not configured: server OPENAI_API_KEY is missing.")
        model = request.model or os.getenv("GEOMIND_VLM_MODEL", "gpt-4.1-mini")
        client = OpenAI(api_key=key)
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[{"role": "user", "content": [
                {"type": "text", "text": build_grounding_prompt(request.question, request.evidence)},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{encoded}", "detail": "high"}},
            ]}],
        )
        return {
            "model": model,
            "answer": response.choices[0].message.content or "",
            "evidence_supplied": bool(request.evidence),
            "warning": "VLM interpretation is not ground truth. GIS measurements must come from validated deterministic tools.",
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"VLM request failed: {exc}") from exc
