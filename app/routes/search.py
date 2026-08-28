from typing import Any, Optional

from fastapi import APIRouter, Query, Request

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search")
async def search(
    request: Request,
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius: float = Query(5.0, gt=0, le=100),
    q: Optional[str] = Query(None),
    sport: Optional[str] = Query(None),
    access: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
) -> dict[str, Any]:
    search_service = request.app.state.search_service
    results = search_service.search(
        latitude=lat, longitude=lon, radius=radius, sport=sport, access=access, query=q
    )
    results = search_service.sort_results(results, sort)

    return {"count": len(results), "radius_miles": radius, "results": results}
