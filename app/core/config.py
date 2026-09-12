"""
Core Application Configuration
Loads environment settings using Pydantic BaseSettings with graceful fallback.
"""

import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import Field

    class Settings(BaseSettings):
        model_config = SettingsConfigDict(env_file=".env", extra="ignore")

        PROJECT_NAME: str = Field(default="Airport Digital Helpdesk Backend")
        VERSION: str = Field(default="7.3.8")
        ENVIRONMENT: str = Field(default="development")
        PORT: int = Field(default=5000)
        WORKERS: int = Field(default=1)
        REDIS_URL: Optional[str] = Field(default=None)
        DATABASE_URL: str = Field(default="sqlite:///./app.db")
        GROQ_API_KEY: str = Field(default="")
        RECORDINGS_DIR: str = Field(default="recordings")

    settings = Settings()

except Exception:
    class SettingsFallback:
        PROJECT_NAME: str = "Airport Digital Helpdesk Backend"
        VERSION: str = "7.3.8"
        ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
        PORT: int = int(os.getenv("PORT", "5000"))
        WORKERS: int = int(os.getenv("WORKERS", "1"))
        REDIS_URL: Optional[str] = os.getenv("REDIS_URL", None)
        DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
        GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
        RECORDINGS_DIR: str = os.getenv("RECORDINGS_DIR", "recordings")

    settings = SettingsFallback()
