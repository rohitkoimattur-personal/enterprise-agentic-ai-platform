from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException
from openai import OpenAIError
import logging

logger = logging.getLogger(__name__)

from app.services.ai_investigation import (
    AIInvestigationResult,
    investigate_with_ai,
)

from app.services.investigation import (
    InvestigationRequest,
    InvestigationResult,
    investigate_incident,
)

app = FastAPI(
    title="Enterprise Agentic AI Platform",
    description="Enterprise AI incident investigation and AgentOps",
    version="0.1.0",
)


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service="enterprise-agentic-ai-platform",
        timestamp=datetime.now(timezone.utc),
    )

@app.post(
    "/api/v1/incidents/investigate",
    response_model=InvestigationResult,
    tags=["Incident Investigation"],
)
async def investigate(
    request: InvestigationRequest,
) -> InvestigationResult:
    result = investigate_incident(request.incident_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return result


@app.post(
    "/api/v1/incidents/investigate/ai",
    response_model=AIInvestigationResult,
    tags=["AI Incident Investigation"],
)
async def investigate_ai(
    request: InvestigationRequest,
) -> AIInvestigationResult:
    try:
        result = investigate_with_ai(request.incident_id)
    except OpenAIError as exc:
        logger.error(
        	"OpenAI investigation failed: %s",
        	type(exc).__name__,
    	) 
        raise HTTPException(
            status_code=503,
            detail="AI investigation service unavailable",
        ) from exc

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return result

