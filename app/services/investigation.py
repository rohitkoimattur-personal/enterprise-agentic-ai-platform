from typing import Literal

from pydantic import BaseModel


class InvestigationRequest(BaseModel):
    incident_id: str


class InvestigationResult(BaseModel):
    incident_id: str
    service: str
    severity: str
    status: Literal["completed"]
    probable_cause: str
    evidence: list[str]
    recommended_actions: list[str]


# Mock enterprise data. Replace with real integrations later.
INCIDENTS = {
    "INC001": {
        "service": "payment-service",
        "severity": "P1",
    }
}

TELEMETRY = {
    "payment-service": {
        "cpu_percent": 92,
        "error_rate_percent": 8.5,
        "latency_ms": 2400,
    }
}


def investigate_incident(
    incident_id: str,
) -> InvestigationResult | None:
    incident = INCIDENTS.get(incident_id)

    if incident is None:
        return None

    service = incident["service"]
    telemetry = TELEMETRY[service]

    evidence = [
        f"CPU utilization: {telemetry['cpu_percent']}%",
        f"Error rate: {telemetry['error_rate_percent']}%",
        f"Latency: {telemetry['latency_ms']} ms",
    ]

    if telemetry["cpu_percent"] > 85:
        probable_cause = (
            "High CPU utilization correlated with "
            "elevated latency and error rate"
        )
        actions = [
            "Inspect recent deployments",
            "Review CPU-intensive processes",
            "Evaluate scaling requirements",
        ]
    else:
        probable_cause = "Insufficient evidence"
        actions = ["Collect additional telemetry"]

    return InvestigationResult(
        incident_id=incident_id,
        service=service,
        severity=incident["severity"],
        status="completed",
        probable_cause=probable_cause,
        evidence=evidence,
        recommended_actions=actions,
    )

