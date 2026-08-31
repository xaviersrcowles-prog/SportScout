from typing import Any

from fastapi import APIRouter

from app.models.ai import AccessClassificationRequest
from app.services.access_classifier import deterministic_access_classification
from app.services.ai_service import classify_with_ai

router = APIRouter(prefix="/api", tags=["ai"])


@router.post("/ai/classify-access")
async def classify_access(request: AccessClassificationRequest) -> dict[str, Any]:
    try:
        return await classify_with_ai(request)
    except Exception:
        fallback = deterministic_access_classification(request)
        fallback["ai_error"] = "AI service unavailable; deterministic fallback used."
        return fallback


@router.post("/classify-access")
async def classify_access_legacy(request: AccessClassificationRequest) -> dict[str, Any]:
    """Backwards-compatible alias for the pre-namespaced path."""
    return await classify_access(request)
