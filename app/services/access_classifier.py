"""Deterministic rule-based access classification.

Used as the safe fallback whenever the AI provider is unavailable or
unconfigured, and as the first pass before AI is invoked.
"""

from typing import Any

from app.models.ai import AccessClassificationRequest
from app.utils.normalization import normalize_text

PUBLIC_TAGS = {"yes", "public"}
PRIVATE_TAGS = {"no", "private"}
RESTRICTED_TAGS = {"customers", "permit", "permissive"}


def deterministic_access_classification(request: AccessClassificationRequest) -> dict[str, Any]:
    access_tag = normalize_text(request.access_tag)

    if access_tag in PUBLIC_TAGS:
        return {
            "classification": "public",
            "confidence": 0.85,
            "evidence": f"OSM access tag is '{access_tag}'.",
            "source": "rule",
        }

    if access_tag in PRIVATE_TAGS:
        return {
            "classification": "private",
            "confidence": 0.85,
            "evidence": f"OSM access tag is '{access_tag}'.",
            "source": "rule",
        }

    if access_tag in RESTRICTED_TAGS:
        return {
            "classification": "restricted",
            "confidence": 0.75,
            "evidence": f"OSM access tag is '{access_tag}'.",
            "source": "rule",
        }

    return {
        "classification": "unknown",
        "confidence": 0.0,
        "evidence": "No sufficiently strong access evidence was available.",
        "source": "rule",
    }
