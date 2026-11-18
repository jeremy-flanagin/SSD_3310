from enum import StrEnum

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseBackend(StrEnum):
    DATABASE = "database"
    MEMORY = "memory"

"""Automatically reads config options from .env"""
class Settings(BaseSettings):
    database_debug: bool = False
    database_url: str | None = None
    database_backend: DatabaseBackend = DatabaseBackend.MEMORY

    member_token: str = "member-token"
    admin_token: str = "admin-token"


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def require_database_url_for_database_backend(self) -> "Settings":
        """Require database credentials only when PostgreSQL is selected."""

        if self.database_backend is DatabaseBackend.DATABASE and not self.database_url:
            raise ValueError(
                "DATABASE_URL is required when DATABASE_BACKEND=database"
            )
        return self
