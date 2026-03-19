from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import Settings

_db: AsyncIOMotorDatabase | None = None
_client: AsyncIOMotorClient | None = None


async def init_db() -> AsyncIOMotorDatabase:
    """Инициализация подключения к MongoDB (вызывать при старте приложения)."""
    global _client, _db
    settings = Settings()
    _client = AsyncIOMotorClient(settings.mongodb_url)
    _db = _client[settings.mongodb_database]
    return _db


async def close_db() -> None:
    """Закрытие подключения (вызывать при остановке)."""
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
    _db = None


def get_database() -> AsyncIOMotorDatabase:
    """Возвращает текущее подключение к БД (после init_db)."""
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_db() on startup.")
    return _db


def get_collection_name() -> str:
    """Имя коллекции фильмов."""
    return Settings().mongodb_collection
