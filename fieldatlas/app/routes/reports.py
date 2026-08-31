from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request

from app.models.search import ReportRequest
from app.services.condition_service import condition_from_reports

router = APIRouter(prefix="/api", tags=["reports"])

ALLOWED_REPORT_TYPES = {"condition", "access", "hours", "general"}


@router.post("/facilities/{facility_id}/reports")
async def create_report(request: Request, facility_id: str, report: ReportRequest) -> dict[str, Any]:
    facility_service = request.app.state.facility_service
    repository = request.app.state.repository

    facility = facility_service.get(facility_id)
    if facility is None:
        raise HTTPException(status_code=404, detail="Facility not found.")

    if report.report_type not in ALLOWED_REPORT_TYPES:
        raise HTTPException(status_code=422, detail="Invalid report_type.")

    new_report = {
        "id": f"report_{uuid4().hex[:12]}",
        "facility_id": facility_id,
        "report_type": report.report_type,
        "description": report.description.strip()[:2000],
        "condition": report.condition,
        "status": "received",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    repository.save_report(new_report)

    updated_condition = None
    if report.report_type == "condition":
        facility_reports = repository.reports_for_facility(facility_id)
        updated_condition = condition_from_reports(facility_reports)

    return {
        "message": "Report submitted.",
        "report": new_report,
        "updated_condition": updated_condition,
    }


@router.post("/facilities/{facility_id}/report")
async def create_report_legacy(request: Request, facility_id: str, report: ReportRequest) -> dict[str, Any]:
    """Backwards-compatible alias for the singular /report path."""
    return await create_report(request, facility_id, report)
