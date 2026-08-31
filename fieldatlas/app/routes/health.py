from typing import Any

from fastapi import APIRouter, Request

from app.services.ai_service import is_configured

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health(request: Request) -> dict[str, Any]:
    facility_service = request.app.state.facility_service
    return {
        "status": "ok",
        "facilities_loaded": len(facility_service.list_all()),
        "ai_configured": is_configured(),
    }
