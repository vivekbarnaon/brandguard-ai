from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(alias="DATABASE_URL")
    supabase_url: str = Field(alias="SUPABASE_URL")
    supabase_publishable_key: str = Field(alias="SUPABASE_PUBLISHABLE_KEY")
    supabase_secret_key: SecretStr = Field(alias="SUPABASE_SECRET_KEY")
    supabase_jwt_secret: Optional[SecretStr] = Field(default=None, alias="SUPABASE_JWT_SECRET")
    frontend_url: str = Field(default="http://localhost:3000", alias="FRONTEND_URL")
    aiml_service_url: str = Field(default="http://localhost:8001", alias="AIML_SERVICE_URL")
    aiml_analyze_path: str = Field(default="/analyze", alias="AIML_ANALYZE_PATH")
    aiml_suggestions_path: str = Field(default="/suggestions", alias="AIML_SUGGESTIONS_PATH")
    aiml_process_path: str = Field(default="/process-document", alias="AIML_PROCESS_PATH")
    aiml_internal_token: Optional[SecretStr] = Field(default=None, alias="AIML_INTERNAL_TOKEN")
    storage_bucket: str = Field(default="brand-guidelines", alias="STORAGE_BUCKET")
    max_upload_bytes: int = Field(default=10 * 1024 * 1024, alias="MAX_UPLOAD_BYTES")

    @field_validator("database_url")
    @classmethod
    def use_async_driver(cls, value: str) -> str:
        return value.replace("postgresql://", "postgresql+asyncpg://", 1)

    @property
    def supabase_issuer(self) -> str:
        return f"{self.supabase_url.rstrip('/')}/auth/v1"

    @property
    def supabase_jwks_url(self) -> str:
        return f"{self.supabase_issuer}/.well-known/jwks.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()

