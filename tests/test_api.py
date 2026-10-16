from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_catalog_rejects_reversed_dates():
    response = client.post("/api/catalog/sentinel-2", json={
        "west": 77.2, "south": 28.4, "east": 77.55, "north": 28.65,
        "start_date": "2025-05-01", "end_date": "2025-04-01",
        "max_cloud_cover": 30, "limit": 10,
    })
    assert response.status_code == 422
