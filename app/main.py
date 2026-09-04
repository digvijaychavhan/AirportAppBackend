"""
Main Application Bootstrap & ASGI Entrypoint
Powered by FastAPI, SQLAlchemy & Socket.IO for real-time WebRTC signaling.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import socketio

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.db.migrations import run_migrations
from app.db.seed.seeder import seed_database
import asyncio
from app.modules import all_routers
from app.modules.support.service import sio, get_recordings_dir
from app.modules.hardware.service import start_hardware_monitoring, stop_hardware_monitoring

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup & shutdown events.
    Executes idempotent migrations, initial seed population, and hardware monitors.
    """
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    try:
        run_migrations()
        seed_database(force=False)
        from app.modules.wayfinding.service import pathfinding_engine
        pathfinding_engine.get_or_build_graph(accessibility_mode="elevator")
        pathfinding_engine.get_or_build_graph(accessibility_mode="escalator")
        logger.info("Pathfinding graphs pre-warmed successfully")
    except Exception as e:
        logger.error(f"Startup database initialization warning: {e}")

    # Start physical barcode scanner & hardware monitoring
    try:
        loop = asyncio.get_running_loop()
        start_hardware_monitoring(loop)
    except Exception as e:
        logger.warning(f"Hardware monitoring startup warning: {e}")

    yield

    stop_hardware_monitoring()
    logger.info(f"Shutting down {settings.PROJECT_NAME}")

def create_app() -> FastAPI:
    """
    FastAPI Application Factory
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # 1. CORS Middleware - Support all origins (Vercel, custom domains, IP endpoints, LAN, and localhost)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_origin_regex=r".*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # 2. Base Health Check Endpoints (Support both GET and HEAD methods)
    @app.api_route("/", methods=["GET", "HEAD"], tags=["Health"])
    @app.api_route("/health", methods=["GET", "HEAD"], tags=["Health"])
    async def health_check():
        return {
            "status": "online",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT
        }

    # 3. Mount all domain module routers
    for router in all_routers:
        app.include_router(router)

    # 4. Mount Call Recordings Directory
    recordings_dir = get_recordings_dir()
    app.mount("/recordings", StaticFiles(directory=recordings_dir), name="recordings")

    return app

fastapi_app = create_app()

# Wrap FastAPI app with Socket.IO ASGI server
combined_app = socketio.ASGIApp(sio, fastapi_app)
app = combined_app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:combined_app", host="0.0.0.0", port=settings.PORT, reload=True)
