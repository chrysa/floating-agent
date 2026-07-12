"""Floating Agent — optional FastAPI HTTP layer (enabled via `--serve`).

The primary shell is the native PySide6 overlay, which calls the plugins/agent core
directly in-process (no HTTP). This FastAPI app only exists to optionally expose the
agent to other chrysa tools. Listens on 127.0.0.1:34001 (localhost only, never exposed).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from floating_agent.api.routers import alerts, health, system

DAEMON_VERSION = "0.1.0"
DAEMON_PORT = 34001

app = FastAPI(
    title="Floating Agent Daemon",
    version=DAEMON_VERSION,
    description="Python sidecar for system monitoring and integrations",
    docs_url="/docs",
    redoc_url=None,
)

# Localhost-only origins (the optional HTTP layer is never exposed externally)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(system.router, prefix="/system", tags=["system"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
