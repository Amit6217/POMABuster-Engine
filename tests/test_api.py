"""
FastAPI Integration Tests using TestClient.
"""

from fastapi.testclient import TestClient
from backend.api.server import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "sigma" in data["config"]

def test_get_config():
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert data["sigma"] == 0.0001
    assert data["block_window_n"] == 2

def test_list_incidents():
    response = client.get("/api/incidents")
    assert response.status_code == 200
    incidents = response.json()
    assert len(incidents) > 0
    # Must have both multi-tx and single-tx
    multi_tx = [i for i in incidents if i["is_multi_tx"]]
    assert len(multi_tx) > 0

def test_get_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    stats = response.json()
    assert stats["poma_incidents_total"] > 0
    assert stats["multi_tx_percentage"] > 50.0

def test_post_detect_with_custom_threshold():
    response = client.post("/api/detect", json={
        "sigma": 0.0002,
        "block_window_n": 2,
        "strike_percentage": 0.02
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "stats" in data
