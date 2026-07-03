import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    EduPilot AI settings class using Pydantic Settings.
    Loads variables from the environment or from the .env file.
    """
    GROQ_API_KEY: str = "gsk_mock_key_for_setup_replace_me"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    BACKEND_URL: str = "http://127.0.0.1:8000"
    DATABASE_URL: str = "sqlite:///./campuspilot.db"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate settings to be imported across the project
settings = Settings()
