# D:/AI/ai-scout/browser-use/backend/main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import api_router
from backend.config import settings
from backend.database import init_db
from backend.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # On startup
    logger.info("Starting Browser-Use WebUI...")
    await init_db()
    logger.info("Database initialized")

    yield

    # On shutdown
    logger.info("Shutting down Browser-Use WebUI...")


# Create app
app = FastAPI(
    title="Browser-Use WebUI",
    description="Scheduled Task Data Collection System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Root path"""
    return {
        "name": "Browser-Use WebUI",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
