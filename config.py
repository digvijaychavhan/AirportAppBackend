import os

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field

    class Settings(BaseSettings):
        PORT: int = Field(default=5000)
        ENVIRONMENT: str = Field(default="development")
        DATABASE_URL: str = Field(default="sqlite:///./app.db")
        GROQ_API_KEY: str = Field(default="")

        class Config:
            env_file = ".env"
            extra = "ignore"

    settings = Settings()

except Exception:
    class SettingsFallback:
        PORT = int(os.getenv("PORT", "5000"))
        ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
        GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

    settings = SettingsFallback()
