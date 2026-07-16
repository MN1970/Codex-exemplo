"""
Portal Master — Codex-exemplo
Central registry and API for Manta Maestro v5.0 5-Layer Architecture
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from app.db import init_db
from app.core.config import get_security_settings
from app.core.security import get_current_user
from app.middleware.auth_middleware import AuthMiddleware
from app.routers import agents, github, maestro, knowledge, auth

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    Startup: Initialize database
    Shutdown: Cleanup (if needed)
    """
    logger.info("Starting up Portal Master...")
    init_db()
    logger.info("Database initialized successfully")
    yield
    logger.info("Shutting down Portal Master")


app = FastAPI(
    title="Portal Master — Codex-exemplo",
    version="0.1.0-portal-adk5",
    description="Central registry and API for ADK-5 Layer Architecture",
    lifespan=lifespan
)

# CORS middleware
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication middleware
settings = get_security_settings()
app.add_middleware(AuthMiddleware, excluded_paths=settings.EXCLUDED_PATHS)

# Include routers
app.include_router(auth.router)
app.include_router(agents.router)
app.include_router(github.router)
app.include_router(maestro.router)
app.include_router(knowledge.router)

@app.get("/api/health", tags=["Health"])
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "portal-master",
        "version": "0.1.0-portal-adk5"
    }

@app.get("/api/config", tags=["Configuration"])
async def get_config():
    """Get portal configuration."""
    return {
        "adk_version": 5,
        "layers": [
            "User Interface",
            "Orchestration & Routing",
            "Domain Expertise (Vertical Agents)",
            "Cross-Domain Services (Horizontal Agents)",
            "Infrastructure (Portal Registry & Sync)"
        ],
        "agent_count": 20,
        "tool_count": 14
    }

@app.get("/api/config/webhooks", tags=["Configuration"])
async def get_webhook_config():
    """Get webhook configuration status."""
    webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    portal_integration = os.getenv(
        "PORTAL_INTEGRATION_URL",
        "http://localhost:8016"
    )

    return {
        "webhooks": {
            "github": {
                "enabled": bool(webhook_secret),
                "endpoint": "/api/webhooks/github",
                "integration_url": portal_integration,
                "supported_events": ["push", "pull_request", "issues", "release"]
            }
        }
    }

@app.get("/api/agents", tags=["Agents"])
async def list_agents():
    """List all registered agents."""
    return {
        "agents": [],
        "count": 0,
        "status": "Coming soon"
    }

@app.post("/api/sync/pull", tags=["Synchronization"])
async def sync_pull(current_user: dict = Depends(get_current_user)):
    """Pull agent metadata from Manta Hub. Requires authentication."""
    logger.info(f"Sync pull requested by user: {current_user.get('sub')}")
    return {
        "status": "pending",
        "message": "Sync implementation coming soon"
    }

@app.post("/api/sync/push", tags=["Synchronization"])
async def sync_push(current_user: dict = Depends(get_current_user)):
    """Push agent metadata to Manta Hub. Requires authentication."""
    logger.info(f"Sync push requested by user: {current_user.get('sub')}")
    return {
        "status": "pending",
        "message": "Sync implementation coming soon"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=True
    )
