from enum import StrEnum

from pydantic import model_validator
from pydantic.v1 import BaseSettings
from pydantic_settings import SettingsConfigDict


class DatabaseBackend(StrEnum):
    DATABASE = "database"
    MEMORY = "memory"

"""Automatically reads config options from .env"""
class Settings(BaseSettings):
    database_debug: bool = False
    database_url: str | None = None
    database_backend: DatabaseBackend = DatabaseBackend.MEMORY

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )