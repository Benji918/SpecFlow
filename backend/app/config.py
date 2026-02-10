from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL")

    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Ollama
    OLLAMA_API_KEY: str = os.getenv("OLLAMA_API_KEY")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL")

    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND")

    # App
    APP_NAME: str = "SpecFlow"
    DEBUG: bool = True
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
