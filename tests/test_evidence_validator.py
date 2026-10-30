from types import SimpleNamespace

from app.services.evidence_validator import (
    validate_investigation,
)


def make_report(
    probable_cause="Possible CPU saturation",
    evidence=None,
    limitations=None,
):
    return SimpleNamespace(
        probable_cause=probable_cause,
        evidence=evidence or ["CPU usage is 92%"],
        limitations=limitations or [
            "No deployment history available"
        ],
    )


def make_tool_evidence():
    return {
        "get_telemetry": {
            "cpu_percent": 92,
            "error_rate_percent": 8.5,
            "latency_ms": 2400,
        },
        "search_runbooks": {
            "service": "payment-service",
            "runbooks": [
                "Inspect CPU saturation and thread pools."
            ],
        },
    }


def test_valid_report_passes():
    report = make_report(
        evidence=[
            "CPU usage is 92%",
            "Error rate is 8.5%",
            "Latency is 2400 ms",
        ]
    )

    result = validate_investigation(
        report, make_tool_evidence()
    )

    assert result.valid is True
    assert result.issues == []


def test_missing_telemetry_claim_rejected():
    report = make_report(
        probable_cause="No telemetry available"
    )

    result = validate_investigation(
        report, make_tool_evidence()
    )

    assert result.valid is False
    assert any(
        "telemetry" in issue.lower()
        for issue in result.issues
    )


def test_wrong_cpu_metric_rejected():
    report = make_report(
        evidence=["CPU usage is 45%"]
    )

    result = validate_investigation(
        report, make_tool_evidence()
    )

    assert result.valid is False
    assert any(
        "cpu_percent" in issue
        for issue in result.issues
    )


def test_missing_runbook_claim_rejected():
    report = make_report(
        limitations=["No runbooks found"]
    )

    result = validate_investigation(
        report, make_tool_evidence()
    )

    assert result.valid is False
    assert any(
        "runbooks" in issue.lower()
        for issue in result.issues
    )


def test_missing_evidence_does_not_imply_successful_retrieval():
    report = make_report(
        probable_cause="No telemetry available"
    )

    result = validate_investigation(report, {})

    # No successful retrieval was recorded.
    # This specific contradiction cannot be established.
    assert result.valid is True

