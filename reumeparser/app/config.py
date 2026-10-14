"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the API and extraction service."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-3.5-flash-lite", alias="GEMINI_MODEL")
    max_upload_size_mb: int = Field(default=10, alias="MAX_UPLOAD_SIZE_MB", ge=1, le=50)
    upload_dir: str = Field(default="data/uploads", alias="UPLOAD_DIR")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Return the cached process settings."""

    return Settings()

