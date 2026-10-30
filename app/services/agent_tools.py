from app.services.investigation import INCIDENTS, TELEMETRY

RUNBOOKS = {
    "payment-service": [
        "Check recent application deployments.",
        "Inspect CPU saturation and thread pools.",
        "Compare error rates with latency changes.",
        "Consider scaling only after verifying the bottleneck.",
    ]
}


def get_incident(incident_id: str) -> dict:
    incident = INCIDENTS.get(incident_id)
    if incident is None:
        return {"error": "Incident not found"}

    return {"incident_id": incident_id, **incident}


def get_telemetry(service: str) -> dict:
    return TELEMETRY.get(
        service, {"error": "Telemetry not found"}
    )


def search_runbooks(service: str) -> dict:
    return {
        "service": service,
        "runbooks": RUNBOOKS.get(service, []),
    }


TOOL_FUNCTIONS = {
    "get_incident": get_incident,
    "get_telemetry": get_telemetry,
    "search_runbooks": search_runbooks,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "get_incident",
        "description": "Retrieve incident details by ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "incident_id": {"type": "string"}
            },
            "required": ["incident_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_telemetry",
        "description": "Retrieve metrics for a service.",
        "parameters": {
            "type": "object",
            "properties": {
                "service": {"type": "string"}
            },
            "required": ["service"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "search_runbooks",
        "description": "Find operational runbooks for a service.",
        "parameters": {
            "type": "object",
            "properties": {
                "service": {"type": "string"}
            },
            "required": ["service"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

