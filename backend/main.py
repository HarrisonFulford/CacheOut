import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.routes import router
from backend.scheduler import Scheduler
from backend.config import config
from backend.logger import logger

# Global scheduler instance
scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    # Startup
    logger.info("Starting CacheOut coordinator...")
    scheduler = Scheduler()
    logger.info("CacheOut coordinator started successfully")
    yield
    # Shutdown
    logger.info("Shutting down CacheOut coordinator...")

app = FastAPI(
    title="CacheOut Coordinator",
    description="Distributed compute marketplace coordinator",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    ) 