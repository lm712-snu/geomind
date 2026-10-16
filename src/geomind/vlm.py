"""Optional OpenAI-compatible vision-language integration.

Requires OPENAI_API_KEY and the optional `vlm` dependency. No API key is stored
in the repository. The model's answer remains an interpretation; GIS numbers must
come from deterministic tools and be recorded separately in GeoProof.
"""
from __future__ import annotations

import base64
import json
import mimetypes
import os
from pathlib import Path
from typing import Any


class VLMError(RuntimeError):
    """Raised when VLM inference is unavailable or fails."""


def build_grounding_prompt(question: str, evidence: dict[str, Any] | None = None) -> str:
    evidence_text = json.dumps(evidence or {}, indent=2, ensure_ascii=False)
    return f"""You are GeoMind, a cautious geospatial research assistant.
Answer the user's question only to the extent supported by the supplied image and
evidence. Do not invent acquisition dates, coordinates, areas, pixel counts, model
metrics, or changes. Numeric GIS claims must be copied from the evidence object;
if a requested value is absent, say that a GIS tool must calculate it. Clearly
separate (1) directly visible observations, (2) interpretations, and (3) unknowns.
Mention relevant limitations such as resolution, cloud/shadow, season, and missing
metadata. Do not claim that a map basemap is a live satellite feed.

Question:
{question}

GeoMind evidence (may be empty; not all fields imply ground truth):
{evidence_text}
"""


def answer_image_question(
    image_path: str | Path,
    question: str,
    *,
    evidence: dict[str, Any] | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> dict[str, str]:
    """Ask a hosted vision-language model about a local image.

    Returns model name and answer. For the experiment, call this same function and
    same model settings for image-only (evidence=None) and grounded conditions.
    """
    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise VLMError("Set OPENAI_API_KEY in your environment; do not commit it.")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise VLMError("Install optional dependency: pip install -e '.[vlm]'") from exc

    path = Path(image_path)
    if not path.is_file():
        raise VLMError(f"Image not found: {path}")
    mime, _ = mimetypes.guess_type(path.name)
    if mime not in {"image/png", "image/jpeg", "image/webp", "image/gif"}:
        raise VLMError("Use a PNG, JPEG, WEBP, or GIF preview image for VLM inference.")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    model_name = model or os.environ.get("GEOMIND_VLM_MODEL", "gpt-4.1-mini")
    prompt = build_grounding_prompt(question, evidence)
    client = OpenAI(api_key=key)
    try:
        response = client.chat.completions.create(
            model=model_name,
            temperature=0,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"data:{mime};base64,{encoded}", "detail": "high"
                    }},
                ],
            }],
        )
        answer = response.choices[0].message.content or ""
        return {"model": model_name, "answer": answer}
    except Exception as exc:
        raise VLMError(f"Vision-language inference failed: {exc}") from exc
