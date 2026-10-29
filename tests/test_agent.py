
from unittest.mock import MagicMock,patch

from types import SimpleNamespace
from fastapi.testclient import TestClient
from app.services.agent import run_agent
from app.services.agent_tools import TOOL_FUNCTIONS

from app.main import app
from app.services.agent import AgentInvestigationResult
from app.services.agent_tools import (
    get_incident,
    get_telemetry,
    search_runbooks,
)

client = TestClient(app)


def test_agent_corrects_wrong_service_arguments():
    # Simulate OpenAI supplying incorrect service arguments.
    tool_calls = [
        SimpleNamespace(
            type="function_call",
            name="get_telemetry",
            arguments='{"service": "INC001"}',
            call_id="call_1",
            model_dump=lambda **kwargs: {
                "type": "function_call",
                "name": "get_telemetry",
                "arguments": '{"service": "INC001"}',
                "call_id": "call_1",
            },
        ),
        SimpleNamespace(
            type="function_call",
            name="search_runbooks",
            arguments='{"service": "INC001"}',
            call_id="call_2",
            model_dump=lambda **kwargs: {
                "type": "function_call",
                "name": "search_runbooks",
                "arguments": '{"service": "INC001"}',
                "call_id": "call_2",
            },
        ),
    ]

    first_response = SimpleNamespace(output=tool_calls)
    second_response = SimpleNamespace(output=[])

    final_report = SimpleNamespace(
        output_parsed=__import__(
            "app.services.agent", fromlist=["AgentInvestigationResult"]
        ).AgentInvestigationResult(
            incident_id="INC001",
            probable_cause="Possible CPU saturation",
            confidence=0.7,
            evidence=["CPU utilization is 92%"],
            recommended_actions=["Inspect CPU profiles"],
            limitations=["No deployment history"],
            tools_used=[],
        )
    )

    mock_client = MagicMock()
    mock_client.responses.create.side_effect = [
        first_response,
        second_response,
    ]
    mock_client.responses.parse.return_value = final_report

    original_telemetry = TOOL_FUNCTIONS["get_telemetry"]
    original_runbooks = TOOL_FUNCTIONS["search_runbooks"]

    with (
        patch.dict(
            TOOL_FUNCTIONS,
            {
                "get_telemetry": MagicMock(
                    wraps=original_telemetry
                ),
                "search_runbooks": MagicMock(
                    wraps=original_runbooks
                ),
            },
        )
    ):
        result = run_agent("INC001", client=mock_client)

        TOOL_FUNCTIONS["get_telemetry"].assert_called_once_with(
            service="payment-service"
        )
        TOOL_FUNCTIONS["search_runbooks"].assert_called_once_with(
            service="payment-service"
        )

    assert result.incident_id == "INC001"
    assert "get_telemetry" in result.tools_used
    assert "search_runbooks" in result.tools_used



def test_agent_tools():
    assert get_incident("INC001")["service"] == "payment-service"
    assert get_telemetry("payment-service")["cpu_percent"] == 92
    assert len(search_runbooks("payment-service")["runbooks"]) > 0


def test_agent_endpoint_success():
    report = AgentInvestigationResult(
        incident_id="INC001",
        probable_cause="Possible CPU saturation",
        confidence=0.7,
        evidence=["CPU utilization: 92%"],
        recommended_actions=["Inspect CPU profiles"],
        limitations=["No deployment history"],
        tools_used=["get_incident", "get_telemetry"],
    )

    with patch("app.main.run_agent", return_value=report):
        response = client.post(
            "/api/v1/incidents/investigate/agent",
            json={"incident_id": "INC001"},
        )

    assert response.status_code == 200
    assert "get_incident" in response.json()["tools_used"]


def test_agent_unknown_incident():
    response = client.post(
        "/api/v1/incidents/investigate/agent",
        json={"incident_id": "INC999"},
    )

    assert response.status_code == 404

