import re
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    valid: bool
    issues: list[str] = field(default_factory=list)


def validate_investigation(report, tool_evidence: dict) -> ValidationResult:
    issues = []

    # Check factual statements, not recommended actions.
    statements = [report.probable_cause] + report.evidence + report.limitations
    text = " ".join(statements).lower()

    telemetry = tool_evidence.get("get_telemetry")
    runbooks = tool_evidence.get("search_runbooks")

    if telemetry and "error" not in telemetry:
        missing_telemetry = [
            r"\bno telemetry\b",
            r"\btelemetry (?:is |was )?(?:missing|unavailable)\b",
            r"\babsence of telemetry\b",
        ]
        if any(re.search(pattern, text) for pattern in missing_telemetry):
            issues.append(
                "Report claims telemetry is missing, but telemetry was retrieved."
            )

        # Match each statement independently to avoid crossing metric boundaries.
        metric_patterns = {
            "cpu_percent": [
                r"\bcpu(?: utilization| usage)?\s+(?:is|at)\s+(\d+(?:\.\d+)?)\s*%",
                r"\bcpu(?: utilization| usage)?\s*[:=]\s*(\d+(?:\.\d+)?)\s*%",
                r"\b(\d+(?:\.\d+)?)\s*%\s*cpu\b",
            ],
            "error_rate_percent": [
                r"\berror rate\s+(?:is|at)\s+(\d+(?:\.\d+)?)\s*%",
                r"\berror rate\s*[:=]\s*(\d+(?:\.\d+)?)\s*%",
                r"\b(\d+(?:\.\d+)?)\s*%\s*error rate\b",
            ],
            "latency_ms": [
                r"\blatency\s+(?:is|at)\s+(\d+(?:\.\d+)?)\s*ms\b",
                r"\blatency\s*[:=]\s*(\d+(?:\.\d+)?)\s*ms\b",
                r"\b(\d+(?:\.\d+)?)\s*ms\s*latency\b",
            ],
        }
        for metric, patterns in metric_patterns.items():
            expected = telemetry.get(metric)
            if expected is None:
                continue
            for statement in statements:
                statement_text = statement.lower()
                for pattern in patterns:
                    for match in re.finditer(pattern, statement_text):
                        actual = float(match.group(1))
                        if abs(actual - float(expected)) > 0.001:
                            issues.append(
                                f"{metric}: report says {actual}, "
                                f"tool returned {expected}"
                            )

    if runbooks and "error" not in runbooks and runbooks.get("runbooks"):
        missing_runbooks = [
            r"\bno runbooks?\b",
            r"\brunbooks? (?:are |were )?(?:missing|unavailable)\b",
            r"\babsence of runbooks?\b",
        ]
        if any(re.search(pattern, text) for pattern in missing_runbooks):
            issues.append(
                "Report claims runbooks are missing, but runbooks were retrieved."
            )

    return ValidationResult(valid=len(issues) == 0, issues=issues)

