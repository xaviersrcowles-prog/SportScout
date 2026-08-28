from app.repositories.json_repository import JsonRepository
from app.services.facility_service import FacilityService
from app.services.search_service import SearchService

BOSTON_FACILITY = {
    "id": "f1",
    "name": "Boston Field",
    "sport_types": ["soccer"],
    "latitude": 42.3601,
    "longitude": -71.0589,
    "access": {"classification": "public", "confidence": 0.9},
    "condition": {"status": "good", "score": 80},
    "hours": {},
}

FAR_FACILITY = {
    "id": "f2",
    "name": "Faraway Field",
    "sport_types": ["tennis"],
    "latitude": 45.0,
    "longitude": -93.0,
    "access": {"classification": "private", "confidence": 0.8},
    "condition": {"status": "poor", "score": 20},
    "hours": {},
}


def make_search_service(tmp_path, facilities):
    facilities_file = tmp_path / "facilities.json"
    reports_file = tmp_path / "reports.json"
    facilities_file.write_text(
        '{"metadata": {}, "facilities": ' + __import__("json").dumps(facilities) + "}",
        encoding="utf-8",
    )
    repository = JsonRepository(facilities_file, reports_file)
    return SearchService(FacilityService(repository))


def test_search_excludes_far_results(tmp_path):
    service = make_search_service(tmp_path, [BOSTON_FACILITY, FAR_FACILITY])
    results = service.search(latitude=42.3601, longitude=-71.0589, radius=5)
    ids = [r["id"] for r in results]
    assert "f1" in ids
    assert "f2" not in ids


def test_search_filters_by_sport(tmp_path):
    service = make_search_service(tmp_path, [BOSTON_FACILITY])
    results = service.search(latitude=42.3601, longitude=-71.0589, radius=5, sport="tennis")
    assert results == []


def test_search_includes_distance_and_score(tmp_path):
    service = make_search_service(tmp_path, [BOSTON_FACILITY])
    results = service.search(latitude=42.3601, longitude=-71.0589, radius=5)
    assert results[0]["distance_miles"] == 0.0
    assert "recommendation_score" in results[0]
