import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables once at module import
load_dotenv()

class Config:
    """Centralized configuration for the CacheOut application."""
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Admin Authentication
    ADMIN_TOKEN: str = os.getenv("ADMIN_TOKEN")
    if not ADMIN_TOKEN:
        raise ValueError("ADMIN_TOKEN environment variable is required")
    
    # Worker Configuration
    WORKER_TIMEOUT_SECONDS: int = int(os.getenv("WORKER_TIMEOUT_SECONDS", "60"))
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "100"))
    
    # Job Queue Configuration
    MAX_QUEUE_SIZE: int = int(os.getenv("MAX_QUEUE_SIZE", "1000"))
    JOB_TIMEOUT_SECONDS: int = int(os.getenv("JOB_TIMEOUT_SECONDS", "3600"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./cacheout.db"
    )
    
    # CORS Configuration
    CORS_ORIGINS: list = [
        "http://localhost:5173",  # Vite default port
        "http://localhost:8080",  # Alternative port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://localhost:8888",  # For the HTML test page server
        "http://127.0.0.1:8888"   # For the HTML test page server
    ]
    
    # Credit System
    DEFAULT_STARTING_CREDITS: float = float(os.getenv("DEFAULT_STARTING_CREDITS", "100.0"))
    
    # Job Cost Configuration
    COST_PER_CORE: float = float(os.getenv("COST_PER_CORE", "0.1"))
    COST_PER_100MB_RAM: float = float(os.getenv("COST_PER_100MB_RAM", "0.001"))
    
    # Gemini API Key for Natural Language Processing
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Global config instance
config = Config() 