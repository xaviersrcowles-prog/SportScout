"""Read-side facility lookups on top of the JSON repository."""

from typing import Any, Optional

from app.repositories.json_repository import JsonRepository
from app.utils.normalization import as_list, normalize_text


class FacilityService:
    def __init__(self, repository: JsonRepository):
        self.repository = repository

    def list_all(self) -> list[dict[str, Any]]:
        return self.repository.all_facilities()

    def get(self, facility_id: str) -> Optional[dict[str, Any]]:
        return self.repository.find(facility_id)

    def list_sports(self) -> list[str]:
        sports: set[str] = set()
        for facility in self.repository.all_facilities():
            for sport in as_list(facility.get("sport_types")):
                text = str(sport).strip()
                if text:
                    sports.add(text)
        return sorted(sports, key=str.lower)

    def hours(self, facility_id: str) -> Optional[dict[str, Any]]:
        facility = self.get(facility_id)
        if facility is None:
            return None
        return facility.get("hours", {})

    def condition(self, facility_id: str) -> Optional[dict[str, Any]]:
        facility = self.get(facility_id)
        if facility is None:
            return None
        return facility.get("condition", {"status": "unknown", "score": None, "last_reported": None})

    def matches_sport(self, facility: dict[str, Any], sport: Optional[str]) -> bool:
        if not sport:
            return True
        requested = normalize_text(sport)
        return any(requested in normalize_text(item) for item in as_list(facility.get("sport_types")))

    def matches_access(self, facility: dict[str, Any], access: Optional[str]) -> bool:
        if not access:
            return True
        requested = normalize_text(access)
        access_data = facility.get("access", {})
        classification = (
            access_data.get("classification", "") if isinstance(access_data, dict) else access_data
        )
        return normalize_text(classification) == requested
