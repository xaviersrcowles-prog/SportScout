from typing import Any, Optional

from pydantic import BaseModel


class Access(BaseModel):
    classification: str = "unknown"
    confidence: float = 0.0
    evidence: Optional[str] = None
    source: Optional[str] = None


class Condition(BaseModel):
    status: str = "unknown"
    score: Optional[float] = None
    last_reported: Optional[str] = None


class Facility(BaseModel):
    id: str
    name: str
    sport_types: list[str] = []
    facility_type: Optional[str] = None
    latitude: float
    longitude: float
    address: dict[str, Any] = {}
    access: Access = Access()
    hours: dict[str, Any] = {}
    condition: Condition = Condition()
    surface: Optional[str] = None
    amenities: list[str] = []
    operator: Optional[str] = None
    website: Optional[str] = None
    osm: dict[str, Any] = {}
    sources: list[Any] = []
    updated_at: Optional[str] = None


class FacilitySearchResult(Facility):
    distance_miles: Optional[float] = None
    distance_km: Optional[float] = None
    recommendation_score: Optional[float] = None
