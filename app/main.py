from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException
from openai import OpenAIError
from fastapi.concurrency import run_in_threadpool
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

from app.services.agent import (
    AgentInvestigationResult,
    run_agent,
)
from app.services.investigation import INCIDENTS

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


@app.post(
    "/api/v1/incidents/investigate/agent",
    response_model=AgentInvestigationResult,
    tags=["Agentic AI Investigation"],
    responses={
        404: {"description": "Incident not found"},
        503: {"description": "AI provider unavailable"},
        504: {"description": "Investigation limit exceeded"},
    },
)
async def investigate_with_agent(
    request: InvestigationRequest,
) -> AgentInvestigationResult:
    if request.incident_id not in INCIDENTS:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    try:
        return await run_in_threadpool(
            run_agent, request.incident_id
        )
    except OpenAIError as exc:
        raise HTTPException(
            status_code=503,
            detail="AI provider unavailable",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=504,
            detail="Agent investigation incomplete",
        ) from exc

