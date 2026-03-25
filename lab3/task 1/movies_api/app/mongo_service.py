from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo import ASCENDING

from .schemas import MovieFilterQuery, MovieStatus


MOVIE_FIELDS: List[str] = [
    "title",
    "studio",
    "year",
    "rating",
    "status",
    "actors",
    "director",
    "genre",
]


class MongoService:
    def __init__(self, db: Database, collection_name: str):
        self.collection: Collection = db[collection_name]
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        # Basic indexes for query filters.
        self.collection.create_index([("year", ASCENDING)])
        self.collection.create_index([("rating", ASCENDING)])
        self.collection.create_index([("status", ASCENDING)])
        self.collection.create_index([("director", ASCENDING)])
        self.collection.create_index([("genre", ASCENDING)])
        self.collection.create_index([("actors", ASCENDING)])

    @staticmethod
    def _serialize_movie(doc: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": str(doc["_id"]),
            "title": doc.get("title"),
            "studio": doc.get("studio"),
            "year": doc.get("year"),
            "rating": doc.get("rating"),
            "status": doc.get("status"),
            "actors": doc.get("actors", []),
            "director": doc.get("director"),
            "genre": doc.get("genre"),
        }

    @staticmethod
    def _parse_object_id(movie_id: str) -> ObjectId:
        return ObjectId(movie_id)

    def insert_movie(self, movie: Dict[str, Any]) -> str:
        doc = {k: movie.get(k) for k in MOVIE_FIELDS}
        result = self.collection.insert_one(doc)
        return str(result.inserted_id)

    def get_movie(self, movie_id: str) -> Optional[Dict[str, Any]]:
        oid = self._parse_object_id(movie_id)
        doc = self.collection.find_one({"_id": oid})
        if not doc:
            return None
        return self._serialize_movie(doc)

    def update_movie(self, movie_id: str, movie: Dict[str, Any]) -> bool:
        oid = self._parse_object_id(movie_id)
        doc = {k: movie.get(k) for k in MOVIE_FIELDS}
        result = self.collection.replace_one({"_id": oid}, doc)
        return result.matched_count > 0

    def delete_movie(self, movie_id: str) -> int:
        oid = self._parse_object_id(movie_id)
        result = self.collection.delete_one({"_id": oid})
        return int(result.deleted_count)

    def _build_mongo_filter(self, filters: MovieFilterQuery) -> Dict[str, Any]:
        mongo_filter: Dict[str, Any] = {}

        if filters.year_from is not None or filters.year_to is not None:
            year_range: Dict[str, Any] = {}
            if filters.year_from is not None:
                year_range["$gte"] = filters.year_from
            if filters.year_to is not None:
                year_range["$lte"] = filters.year_to
            mongo_filter["year"] = year_range

        if filters.min_rating is not None:
            mongo_filter["rating"] = {"$gte": filters.min_rating}

        if filters.actor is not None:
            mongo_filter["actors"] = filters.actor

        if filters.director is not None:
            mongo_filter["director"] = filters.director

        if filters.genre is not None:
            mongo_filter["genre"] = filters.genre

        if filters.status is not None:
            # status is stored as string enum value (watched/not_watched).
            mongo_filter["status"] = (
                filters.status.value
                if isinstance(filters.status, MovieStatus)
                else str(filters.status)
            )

        return mongo_filter

    def search_and_count(
        self, filters: MovieFilterQuery
    ) -> Tuple[List[Dict[str, Any]], int]:
        mongo_filter = self._build_mongo_filter(filters)

        total = self.collection.count_documents(mongo_filter)

        cursor = (
            self.collection.find(mongo_filter)
            .skip(filters.offset)
            .limit(filters.limit)
        )
        items = [self._serialize_movie(doc) for doc in cursor]
        return items, int(total)

    def count_only(self, filters: MovieFilterQuery) -> int:
        mongo_filter = self._build_mongo_filter(filters)
        return int(self.collection.count_documents(mongo_filter))

