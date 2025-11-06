"""Campus Manager - Student distribution system."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from core.config import settings
from core.logging import setup_logging, get_logger
from core.lifespan import lifespan
from handlers.http.handler import router

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Student campus distribution management system",
    lifespan=lifespan,
    debug=settings.debug
)

# Configure static files
BASE_DIR = Path(__file__).parent.resolve()
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", tags=["Root"])
async def read_index() -> FileResponse:
    """Serve the main frontend page."""
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Campus Manager is running",
        "version": settings.version,
        "debug": settings.debug
    }


# Include API routers
app.include_router(router)

logger.info(f"Campus Manager starting up - {settings.app_name} v{settings.version}")