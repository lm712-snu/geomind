"""GeoProof evidence records and deterministic verification."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RowEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    row: int = Field(ge=0)
    class_pixels: int = Field(ge=0)
    valid_pixels: int = Field(ge=0)
    pixel_area_m2: float = Field(gt=0, allow_inf_nan=False)


class Measurement(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    value: float | None
    unit: str


class GeoProof(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"] = "1.0"
    question: str
    answer: str
    source_asset: str
    data_kind: Literal["synthetic", "real", "unknown"]
    crs: str
    operation: Literal["class_area"]
    parameters: dict
    measurements: list[Measurement]
    row_evidence: list[RowEvidence]
    assumptions: list[str]
    limitations: list[str]
    verification_status: Literal["verified", "unverified", "failed"]
    created_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def verify_proof(proof: GeoProof) -> Literal["verified", "failed"]:
    """Recompute recorded area from per-row counts and pixel areas; detect value tampering."""
    values = {m.name: m.value for m in proof.measurements}
    if any(r.class_pixels > r.valid_pixels for r in proof.row_evidence):
        return "failed"
    expected_class = sum(r.class_pixels * r.pixel_area_m2 for r in proof.row_evidence)
    expected_valid = sum(r.valid_pixels * r.pixel_area_m2 for r in proof.row_evidence)
    for name, expected in (("class_area", expected_class), ("valid_area", expected_valid)):
        actual = values.get(name)
        if actual is None or abs(actual - expected) > max(1e-6, abs(expected) * 1e-9):
            return "failed"
    proportion = values.get("class_proportion")
    expected_proportion = expected_class / expected_valid if expected_valid > 0 else None
    if expected_proportion is None:
        if proportion is not None:
            return "failed"
    elif proportion is None or abs(proportion - expected_proportion) > 1e-9:
        return "failed"
    return "verified"


def build_class_area_proof(result: dict, question: str, source_asset: str, data_kind: str = "synthetic") -> GeoProof:
    """Build a provenance record from actual deterministic analysis output."""
    if result["status"] != "ok":
        answer = "The proportion is undefined because there are no valid pixels."
    else:
        answer = (f"Class {result['class_value']:g} covers {result['class_area_m2']:.2f} m² "
                  f"({result['class_proportion'] * 100:.2f}% of valid area).")
    proof = GeoProof(
        question=question, answer=answer, source_asset=source_asset, data_kind=data_kind,
        crs=result["crs"], operation="class_area",
        parameters={"class_value": result["class_value"], "status": result["status"]},
        measurements=[
            Measurement(name="class_area", value=result["class_area_m2"], unit="m²"),
            Measurement(name="valid_area", value=result["valid_area_m2"], unit="m²"),
            Measurement(name="class_proportion", value=result["class_proportion"], unit="fraction"),
        ],
        row_evidence=[RowEvidence(**row) for row in result["row_evidence"]],
        assumptions=["Input grid and CRS metadata correctly describe the raster."],
        limitations=[
            "The record proves calculation traceability, not classification correctness.",
            "Synthetic input is a software fixture, not a real satellite observation."
            if data_kind == "synthetic" else
            "Interpretation depends on the source data, class definition, and valid-data mask.",
        ], verification_status="unverified",
    )
    return proof.model_copy(update={"verification_status": verify_proof(proof)})
