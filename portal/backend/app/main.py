"""
Portal Master — Codex-exemplo
Central registry and API for Manta Maestro v5.0 5-Layer Architecture
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Portal Master — Codex-exemplo",
    version="0.1.0-portal-adk5",
    description="Central registry and API for ADK-5 Layer Architecture"
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

@app.get("/api/agents", tags=["Agents"])
async def list_agents():
    """List all registered agents."""
    return {
        "agents": [],
        "count": 0,
        "status": "Coming soon"
    }

@app.post("/api/sync/pull", tags=["Synchronization"])
async def sync_pull():
    """Pull agent metadata from Manta Hub."""
    return {
        "status": "pending",
        "message": "Sync implementation coming soon"
    }

@app.post("/api/sync/push", tags=["Synchronization"])
async def sync_push():
    """Push agent metadata to Manta Hub."""
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
