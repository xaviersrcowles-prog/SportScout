from fastapi.testclient import TestClient

from main import app


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_search_requires_coordinates():
    with TestClient(app) as client:
        response = client.get("/api/search")
        assert response.status_code == 422


def test_search_returns_results_near_boston():
    with TestClient(app) as client:
        response = client.get("/api/search", params={"lat": 42.3601, "lon": -71.0589, "radius": 25})
        assert response.status_code == 200
        body = response.json()
        assert "results" in body
        assert body["count"] == len(body["results"])


def test_facility_not_found():
    with TestClient(app) as client:
        response = client.get("/api/facilities/does-not-exist")
        assert response.status_code == 404


def test_classify_access_falls_back_without_ai_configured():
    with TestClient(app) as client:
        response = client.post(
            "/api/ai/classify-access",
            json={"facility_name": "Test Field", "access_tag": "yes"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["classification"] == "public"
