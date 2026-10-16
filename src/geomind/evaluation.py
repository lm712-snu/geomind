"""Paired evaluation helpers for image-only and evidence-grounded systems.

These functions score supplied predictions against independent references. They do
not generate predictions and must not be used to label synthetic examples as model
performance.
"""
from __future__ import annotations

import math
from collections.abc import Sequence


def exact_match_accuracy(predictions: Sequence[str], references: Sequence[str]) -> float:
    if len(predictions) != len(references) or not references:
        raise ValueError("predictions and references must have equal, non-zero length")
    norm = lambda x: " ".join(str(x).strip().casefold().split())
    return sum(norm(p) == norm(r) for p, r in zip(predictions, references, strict=True)) / len(references)


def numeric_errors(predictions: Sequence[float], references: Sequence[float]) -> dict:
    if len(predictions) != len(references) or not references:
        raise ValueError("predictions and references must have equal, non-zero length")
    pairs = [(float(p), float(r)) for p, r in zip(predictions, references, strict=True)]
    if not all(math.isfinite(p) and math.isfinite(r) for p, r in pairs):
        raise ValueError("numeric predictions and references must be finite")
    errors = [p - r for p, r in pairs]
    abs_errors = [abs(e) for e in errors]
    return {
        "n": len(pairs),
        "mae": sum(abs_errors) / len(abs_errors),
        "rmse": math.sqrt(sum(e * e for e in errors) / len(errors)),
        "bias": sum(errors) / len(errors),
        "absolute_errors": abs_errors,
    }


def paired_binary_comparison(
    baseline_correct: Sequence[bool], grounded_correct: Sequence[bool]
) -> dict:
    """Summarise paired correctness without pretending the result is causal by itself."""
    if len(baseline_correct) != len(grounded_correct) or not baseline_correct:
        raise ValueError("paired correctness arrays must have equal, non-zero length")
    n = len(baseline_correct)
    baseline_acc = sum(bool(x) for x in baseline_correct) / n
    grounded_acc = sum(bool(x) for x in grounded_correct) / n
    baseline_only = sum(bool(b) and not bool(g) for b, g in zip(
        baseline_correct, grounded_correct, strict=True
    ))
    grounded_only = sum(not bool(b) and bool(g) for b, g in zip(
        baseline_correct, grounded_correct, strict=True
    ))
    return {
        "n": n,
        "baseline_accuracy": baseline_acc,
        "grounded_accuracy": grounded_acc,
        "accuracy_delta": grounded_acc - baseline_acc,
        "baseline_only_correct": baseline_only,
        "grounded_only_correct": grounded_only,
        "ties": n - baseline_only - grounded_only,
        "warning": "Descriptive paired summary; add a pre-registered paired test and confidence interval for research claims.",
    }


def unsupported_claim_rate(unsupported: Sequence[bool]) -> float:
    if not unsupported:
        raise ValueError("unsupported must contain at least one audited response")
    return sum(bool(x) for x in unsupported) / len(unsupported)
