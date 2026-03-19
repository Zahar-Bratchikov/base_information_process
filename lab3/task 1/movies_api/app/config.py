from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения."""

    model_config = SettingsConfigDict(env_prefix="APP_", extra="ignore")

    mongodb_url: str = "mongodb://root:root@localhost:27017/"
    mongodb_database: str = "movies_db"
    mongodb_collection: str = "movies"
