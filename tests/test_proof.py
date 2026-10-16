from geomind.analysis import class_area
from geomind.proof import build_class_area_proof, verify_proof


def test_proof_verifies_and_round_trips_json(synthetic_raster):
    result = class_area(synthetic_raster, class_value=1)
    proof = build_class_area_proof(result, "How much class 1 is present?", "synthetic-fixture")
    assert proof.verification_status == "verified"
    restored = type(proof).model_validate_json(proof.model_dump_json())
    assert verify_proof(restored) == "verified"


def test_tampered_measurement_fails_verification(synthetic_raster):
    result = class_area(synthetic_raster, class_value=1)
    proof = build_class_area_proof(result, "Measure class 1", "synthetic-fixture")
    changed = proof.model_copy(deep=True)
    changed.measurements[0].value += 50
    assert verify_proof(changed) == "failed"


def test_impossible_row_counts_fail_verification(synthetic_raster):
    result = class_area(synthetic_raster, class_value=1)
    proof = build_class_area_proof(result, "Measure class 1", "synthetic-fixture")
    changed = proof.model_copy(deep=True)
    changed.row_evidence[0].class_pixels = changed.row_evidence[0].valid_pixels + 1
    assert verify_proof(changed) == "failed"
