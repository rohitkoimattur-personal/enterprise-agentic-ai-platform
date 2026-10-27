from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel

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
