"""Radius search, filtering, distance annotation and recommendation scoring."""

from typing import Any, Optional

from app.config import RECOMMENDATION_WEIGHTS
from app.services.facility_service import FacilityService
from app.utils.geo import bounding_box, coordinates_of, haversine_distance_miles, in_bounding_box

ACCESS_SCORES = {
    "public": 1.0,
    "restricted": 0.6,
    "members_only": 0.4,
    "private": 0.1,
    "unknown": 0.5,
}

CONDITION_SCORES = {
    "excellent": 1.0,
    "good": 0.8,
    "fair": 0.5,
    "poor": 0.2,
    "unknown": 0.5,
}


def _distance_score(distance_miles: float, radius: float) -> float:
    if radius <= 0:
        return 0.0
    return max(0.0, 1.0 - (distance_miles / radius))


def _access_score(facility: dict[str, Any]) -> float:
    access = facility.get("access", {})
    classification = access.get("classification", "unknown") if isinstance(access, dict) else "unknown"
    return ACCESS_SCORES.get(str(classification).lower(), 0.5)


def _condition_score(facility: dict[str, Any]) -> float:
    condition = facility.get("condition", {})
    score = condition.get("score") if isinstance(condition, dict) else None
    if isinstance(score, (int, float)):
        return max(0.0, min(1.0, score / 100.0))
    status = condition.get("status", "unknown") if isinstance(condition, dict) else "unknown"
    return CONDITION_SCORES.get(str(status).lower(), 0.5)


def _hours_score(facility: dict[str, Any]) -> float:
    hours = facility.get("hours", {})
    if isinstance(hours, dict) and hours.get("display"):
        return 1.0 if hours.get("source") == "openstreetmap" else 0.6
    return 0.4


def _confidence_score(facility: dict[str, Any]) -> float:
    access = facility.get("access", {})
    confidence = access.get("confidence", 0.0) if isinstance(access, dict) else 0.0
    try:
        return max(0.0, min(1.0, float(confidence)))
    except (TypeError, ValueError):
        return 0.0


def recommendation_score(facility: dict[str, Any], distance_miles: float, radius: float) -> float:
    weights = RECOMMENDATION_WEIGHTS
    score = (
        _distance_score(distance_miles, radius) * weights["distance"]
        + _access_score(facility) * weights["access"]
        + _condition_score(facility) * weights["condition"]
        + _hours_score(facility) * weights["hours"]
        + _confidence_score(facility) * weights["confidence"]
    )
    return round(score * 100, 1)


class SearchService:
    def __init__(self, facility_service: FacilityService):
        self.facility_service = facility_service

    MAX_RESULTS = 500

    def search(
        self,
        latitude: float,
        longitude: float,
        radius: float,
        sport: Optional[str] = None,
        access: Optional[str] = None,
        query: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        box = bounding_box(latitude, longitude, radius)
        results = []

        for facility in self.facility_service.list_all():
            coordinates = coordinates_of(facility)
            if coordinates is None:
                continue
            facility_lat, facility_lon = coordinates

            if not in_bounding_box(facility_lat, facility_lon, box):
                continue
            if not self.facility_service.matches_sport(facility, sport):
                continue
            if not self.facility_service.matches_access(facility, access):
                continue
            if query and query.strip():
                needle = query.strip().lower()
                if needle not in str(facility.get("name", "")).lower():
                    continue

            distance = haversine_distance_miles(latitude, longitude, facility_lat, facility_lon)
            if distance > radius:
                continue

            enriched = dict(facility)
            enriched["distance_miles"] = round(distance, 2)
            enriched["distance_km"] = round(distance * 1.609344, 2)
            enriched["recommendation_score"] = recommendation_score(facility, distance, radius)
            results.append(enriched)

        results.sort(key=lambda item: item.get("distance_miles", float("inf")))
        return results[: self.MAX_RESULTS]

    def sort_results(self, results: list[dict[str, Any]], sort_by: Optional[str]) -> list[dict[str, Any]]:
        if sort_by == "condition":
            results.sort(key=lambda r: -_condition_score(r))
        elif sort_by == "access_confidence":
            results.sort(key=lambda r: -_confidence_score(r))
        elif sort_by == "recommendation":
            results.sort(key=lambda r: -(r.get("recommendation_score") or 0))
        else:
            results.sort(key=lambda r: r.get("distance_miles", float("inf")))
        return results
