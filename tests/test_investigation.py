
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_investigate_existing_incident():
    response = client.post(
        "/api/v1/incidents/investigate",
        json={"incident_id": "INC001"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["incident_id"] == "INC001"
    assert data["service"] == "payment-service"
    assert data["status"] == "completed"
    assert len(data["evidence"]) == 3
    assert len(data["recommended_actions"]) > 0


def test_investigate_unknown_incident():
    response = client.post(
        "/api/v1/incidents/investigate",
        json={"incident_id": "INC999"},
    )

    assert response.status_code == 404

