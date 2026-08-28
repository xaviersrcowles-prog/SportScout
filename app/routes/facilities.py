from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query, Request

router = APIRouter(prefix="/api", tags=["facilities"])


@router.get("/facilities")
async def list_facilities(request: Request) -> dict[str, Any]:
    facility_service = request.app.state.facility_service
    facilities = facility_service.list_all()
    return {"count": len(facilities), "results": facilities}


@router.get("/facilities/nearby")
async def facilities_nearby(
    request: Request,
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius: float = Query(5.0, gt=0, le=100),
) -> dict[str, Any]:
    search_service = request.app.state.search_service
    results = search_service.search(latitude=lat, longitude=lon, radius=radius)
    return {"count": len(results), "radius_miles": radius, "results": results}


@router.get("/facilities/{facility_id}")
async def get_facility(request: Request, facility_id: str) -> dict[str, Any]:
    facility_service = request.app.state.facility_service
    facility = facility_service.get(facility_id)
    if facility is None:
        raise HTTPException(status_code=404, detail="Facility not found.")
    return facility


@router.get("/facilities/{facility_id}/hours")
async def get_hours(request: Request, facility_id: str) -> dict[str, Any]:
    facility_service = request.app.state.facility_service
    hours = facility_service.hours(facility_id)
    if hours is None:
        raise HTTPException(status_code=404, detail="Facility not found.")
    return hours


@router.get("/facilities/{facility_id}/condition")
async def get_condition(request: Request, facility_id: str) -> dict[str, Any]:
    facility_service = request.app.state.facility_service
    condition = facility_service.condition(facility_id)
    if condition is None:
        raise HTTPException(status_code=404, detail="Facility not found.")
    return condition


@router.get("/sports")
async def get_sports(request: Request) -> dict[str, Any]:
    facility_service = request.app.state.facility_service
    return {"sports": facility_service.list_sports()}
