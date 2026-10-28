from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.ai_investigation import AIInvestigationResult

client = TestClient(app)


def test_ai_investigation_success():
    mock_result = AIInvestigationResult(
        incident_id="INC001",
        service="payment-service",
        probable_cause="CPU saturation may contribute to latency",
        confidence=0.65,
        evidence=["CPU utilization: 92%"],
        recommended_actions=["Inspect CPU profiles"],
        limitations=["No deployment history available"],
    )

    with patch(
        "app.main.investigate_with_ai",
        return_value=mock_result,
    ):
        response = client.post(
            "/api/v1/incidents/investigate/ai",
            json={"incident_id": "INC001"},
        )

    assert response.status_code == 200
    assert response.json()["confidence"] == 0.65


def test_ai_investigation_unknown_incident():
    with patch(
        "app.main.investigate_with_ai",
        return_value=None,
    ):
        response = client.post(
            "/api/v1/incidents/investigate/ai",
            json={"incident_id": "INC999"},
        )

    assert response.status_code == 404

