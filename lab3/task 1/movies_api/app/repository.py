from __future__ import annotations

from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_collection_name
from app.schemas import MovieCreate, MovieFilters, MovieUpdate


def _filters_to_query(filters: MovieFilters | None) -> dict[str, Any]:
    """Преобразует критерии фильтрации в запрос MongoDB."""
    if not filters:
        return {}
    query: dict[str, Any] = {}
    if filters.year_from is not None:
        query.setdefault("year", {})["$gte"] = filters.year_from
    if filters.year_to is not None:
        query.setdefault("year", {})["$lte"] = filters.year_to
    if filters.rating_min is not None:
        query["rating"] = query.get("rating", {})
        if isinstance(query["rating"], dict):
            query["rating"]["$gte"] = filters.rating_min
        else:
            query["rating"] = {"$gte": filters.rating_min}
    if filters.actor is not None and filters.actor.strip():
        query["actors"] = filters.actor.strip()
    if filters.director is not None and filters.director.strip():
        query["director"] = filters.director.strip()
    if filters.genre is not None and filters.genre.strip():
        query["genre"] = filters.genre.strip()
    if filters.status is not None:
        query["status"] = filters.status
    return query


def _doc_to_movie(doc: dict[str, Any]) -> dict[str, Any]:
    """Добавляет id из _id и приводит документ к формату ответа."""
    out = dict(doc)
    out["id"] = str(doc["_id"])
    del out["_id"]
    return out


async def create_movie(db: AsyncIOMotorDatabase, data: MovieCreate) -> dict[str, Any]:
    """Добавляет фильм в БД."""
    coll = db[get_collection_name()]
    doc = data.model_dump()
    result = await coll.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _doc_to_movie(doc)


async def get_movie_by_id(db: AsyncIOMotorDatabase, movie_id: str) -> dict[str, Any] | None:
    """Возвращает фильм по id или None."""
    if not ObjectId.is_valid(movie_id):
        return None
    coll = db[get_collection_name()]
    doc = await coll.find_one({"_id": ObjectId(movie_id)})
    if not doc:
        return None
    return _doc_to_movie(doc)


async def update_movie(
    db: AsyncIOMotorDatabase, movie_id: str, data: MovieUpdate
) -> dict[str, Any] | None:
    """Обновляет фильм. Возвращает обновлённый документ или None."""
    if not ObjectId.is_valid(movie_id):
        return None
    payload = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    if not payload:
        return await get_movie_by_id(db, movie_id)
    coll = db[get_collection_name()]
    result = await coll.find_one_and_update(
        {"_id": ObjectId(movie_id)},
        {"$set": payload},
        return_document=True,
    )
    if not result:
        return None
    return _doc_to_movie(result)


async def delete_movie(db: AsyncIOMotorDatabase, movie_id: str) -> bool:
    """Удаляет фильм. Возвращает True, если удалён."""
    if not ObjectId.is_valid(movie_id):
        return False
    coll = db[get_collection_name()]
    result = await coll.delete_one({"_id": ObjectId(movie_id)})
    return result.deleted_count > 0


async def list_movies(
    db: AsyncIOMotorDatabase,
    filters: MovieFilters | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Список фильмов с опциональной фильтрацией."""
    coll = db[get_collection_name()]
    query = _filters_to_query(filters)
    cursor = coll.find(query).skip(skip).limit(limit)
    return [_doc_to_movie(d) async for d in cursor]


async def count_movies(
    db: AsyncIOMotorDatabase,
    filters: MovieFilters | None = None,
) -> int:
    """Подсчёт числа фильмов по критериям."""
    coll = db[get_collection_name()]
    query = _filters_to_query(filters)
    return await coll.count_documents(query)
