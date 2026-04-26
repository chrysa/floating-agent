"""Floating Agent daemon — FastAPI sidecar for the Electron shell.

Listens on 127.0.0.1:34001 (localhost only, never exposed externally).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from floating_agent.api.routers import health, system

DAEMON_VERSION = "0.1.0"
DAEMON_PORT = 34001

app = FastAPI(
    title="Floating Agent Daemon",
    version=DAEMON_VERSION,
    description="Python sidecar for system monitoring and integrations",
    docs_url="/docs",
    redoc_url=None,
)

# Allow only Electron renderer (file:// or localhost dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "file://"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(system.router, prefix="/system", tags=["system"])
