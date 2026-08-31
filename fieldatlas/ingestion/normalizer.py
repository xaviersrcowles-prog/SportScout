"""Turn a raw OSM element (tags + resolved coordinates) into an app-ready facility record."""

from datetime import datetime, timezone
from typing import Any, Optional

from app.services.access_classifier import deterministic_access_classification
from app.models.ai import AccessClassificationRequest
from ingestion.osm_filters import facility_type_for


def _sport_types(tags: dict[str, str]) -> list[str]:
    raw = tags.get("sport", "")
    if not raw:
        return []
    return [part.strip() for part in raw.split(";") if part.strip()]


def _amenities(tags: dict[str, str]) -> list[str]:
    amenities = []
    if tags.get("lit") == "yes":
        amenities.append("lighting")
    if tags.get("covered") == "yes":
        amenities.append("covered")
    if tags.get("wheelchair") == "yes":
        amenities.append("wheelchair_accessible")
    if tags.get("changing_room") == "yes":
        amenities.append("changing_room")
    return amenities


def normalize_element(
    element_type: str,
    element_id: int,
    tags: dict[str, str],
    latitude: float,
    longitude: float,
) -> dict[str, Any]:
    name = tags.get("name") or "Unnamed facility"

    classification_request = AccessClassificationRequest(
        facility_name=name,
        description=tags.get("description", ""),
        access_tag=tags.get("access"),
        operator=tags.get("operator"),
    )
    access_result = deterministic_access_classification(classification_request)

    opening_hours = tags.get("opening_hours")

    return {
        "id": f"osm_{element_type}_{element_id}",
        "name": name,
        "sport_types": _sport_types(tags),
        "facility_type": facility_type_for(tags),
        "latitude": latitude,
        "longitude": longitude,
        "address": {
            "street": tags.get("addr:street"),
            "housenumber": tags.get("addr:housenumber"),
            "city": tags.get("addr:city"),
            "state": tags.get("addr:state"),
            "postcode": tags.get("addr:postcode"),
        },
        "access": {
            "classification": access_result["classification"],
            "confidence": access_result["confidence"],
            "evidence": access_result["evidence"],
            "source": access_result["source"],
        },
        "hours": {
            "raw": opening_hours,
            "display": opening_hours,
            "source": "openstreetmap" if opening_hours else None,
        },
        "condition": {"status": "unknown", "score": None, "last_reported": None},
        "surface": tags.get("surface"),
        "amenities": _amenities(tags),
        "operator": tags.get("operator"),
        "website": tags.get("website") or tags.get("contact:website"),
        "osm": {"type": element_type, "id": element_id, "tags": tags},
        "sources": ["openstreetmap"],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
