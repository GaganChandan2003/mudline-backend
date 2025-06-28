from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # Required environment variables with defaults
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = False
    
    # Application info with defaults
    APP_NAME: str = "Mudline Backend"
    APP_VERSION: str = "1.0.0"

    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000"
    ]

    # Pydantic Settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.
    This function is cached to prevent reloading .env file on every request.
    """
    return Settings()


# Create a single instance to import anywhere
settings = get_settings()