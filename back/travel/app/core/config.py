from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List
import os
from pathlib import Path

# Compute the path to .env file
_env_file = Path(__file__).parent.parent.parent / ".env"

class Settings(BaseSettings):
    # App settings
    app_name: str = "travel"
    version: str = "1.0.0"
    description: str = "A FastAPI application created with fastapi-init"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/booking_db"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "app.log"
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    model_config = ConfigDict(
        env_file=str(_env_file),
        env_file_encoding="utf-8",
        case_sensitive=False,  # Changed to False to match .env var names
        extra="ignore"
    )

settings = Settings()