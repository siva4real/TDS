"""Application configuration management using pydantic-settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, SecretStr, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed configuration pulled from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_secret: SecretStr = Field(..., alias="APP_SECRET", description="Shared secret for verifying requests")
    github_token: SecretStr = Field(..., alias="GITHUB_TOKEN", description="Fine-grained PAT with repo/pages scopes")
    github_owner: str = Field(..., alias="GITHUB_OWNER", description="GitHub username or org that will own repos")
    github_pages_branch: str = Field("gh-pages", alias="GITHUB_PAGES_BRANCH")
    default_branch: str = Field("main", alias="DEFAULT_BRANCH")
    llm_model: str = Field("gpt-4o-mini", alias="LLM_MODEL")
    llm_temperature: float = Field(0.2, alias="LLM_TEMPERATURE", ge=0.0, le=1.0)
    work_dir: Path = Field(Path("./workspace"), alias="WORK_DIR")
    database_url: str = Field("sqlite:///./data/app.db", alias="DATABASE_URL")
    evaluation_timeout_seconds: int = Field(600, alias="EVALUATION_TIMEOUT_SECONDS", ge=60)
    evaluation_retry_attempts: int = Field(5, alias="EVALUATION_RETRY_ATTEMPTS", ge=1)
    evaluation_retry_backoff: float = Field(2.0, alias="EVALUATION_RETRY_BACKOFF", ge=1.0)
    github_api_url: str = Field("https://api.github.com", alias="GITHUB_API_URL")
    openai_api_base: Optional[str] = Field(None, alias="OPENAI_API_BASE")

    @validator("work_dir", pre=True)
    def _expand_work_dir(cls, value: str | Path) -> Path:  # noqa: D401
        """Ensure the workspace directory is absolute and exists."""

        path = Path(value).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance to avoid repeated env parsing."""

    return Settings()


settings = get_settings()

