"""
Configuration management for Fiscal Pilot
"""
import os
from pathlib import Path
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Flask
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    PORT: int = int(os.getenv("PORT", "5000"))
    
    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "fiscal_pilot")
    
    # Groq API
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Plaid API (Sandbox - Demo Only, Not RBI Account Aggregator)
    # NOTE: This is Plaid sandbox for demonstration purposes only.
    # In production, this would be replaced with RBI Account Aggregator framework.
    PLAID_CLIENT_ID: str = os.getenv("PLAID_CLIENT_ID", "")
    PLAID_SECRET: str = os.getenv("PLAID_SECRET", "")
    PLAID_ENV: str = os.getenv("PLAID_ENV", "sandbox")  # Must be 'sandbox' for demo
    
    # Application
    UPLOAD_FOLDER: str = str(BASE_DIR / "uploads")
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB max file size
    
    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields in .env file (like FLASK_APP, FLASK_ENV)
    )


# Global settings instance
settings = Settings()

# SQLAlchemy database URI (URL encode password to handle special characters)
# Note: quote_plus encodes special characters in password
encoded_password = quote_plus(settings.DB_PASSWORD) if settings.DB_PASSWORD else ""
DATABASE_URI = (
    f"mysql+pymysql://{settings.DB_USER}:{encoded_password}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    f"?charset=utf8mb4"
)
