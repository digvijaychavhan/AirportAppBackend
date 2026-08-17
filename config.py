import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "app.db")
DEFAULT_DB_URL = f"sqlite:///{DEFAULT_DB_PATH.replace(os.sep, '/')}"

def normalize_db_url(url: str) -> str:
    if not url:
        return DEFAULT_DB_URL
    if url.startswith("sqlite:///./") or url.startswith("sqlite:////./") or url == "sqlite:///app.db":
        clean = url.replace("sqlite:////./", "").replace("sqlite:///./", "").replace("sqlite:///", "")
        abs_p = os.path.join(BASE_DIR, clean)
        return f"sqlite:///{abs_p.replace(os.sep, '/')}"
    return url

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field

    class Settings(BaseSettings):
        PORT: int = Field(default=5000)
        ENVIRONMENT: str = Field(default="development")
        DATABASE_URL: str = Field(default=DEFAULT_DB_URL)
        GROQ_API_KEY: str = Field(default="")

        class Config:
            env_file = os.path.join(BASE_DIR, ".env")
            extra = "ignore"

    settings = Settings()
    settings.DATABASE_URL = normalize_db_url(settings.DATABASE_URL)

except Exception:
    class SettingsFallback:
        PORT = int(os.getenv("PORT", "5000"))
        ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        DATABASE_URL = normalize_db_url(os.getenv("DATABASE_URL", DEFAULT_DB_URL))
        GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

    settings = SettingsFallback()
