from __future__ import annotations

import os

from pydantic import BaseModel


class Settings(BaseModel):
    mongo_host: str = "localhost"
    mongo_port: int = 27017
    mongo_db: str = "movies_db"
    mongo_collection: str = "movies"
    mongo_server_selection_timeout_ms: int = 5000
    mongo_connect_timeout_ms: int = 5000


def load_settings() -> Settings:
    return Settings(
        mongo_host=os.getenv("MONGO_HOST", "localhost"),
        mongo_port=int(os.getenv("MONGO_PORT", "27017")),
        mongo_db=os.getenv("MONGO_DB", "movies_db"),
        mongo_collection=os.getenv("MONGO_COLLECTION", "movies"),
        mongo_server_selection_timeout_ms=int(
            os.getenv("MONGO_SERVER_SELECTION_TIMEOUT_MS", "5000")
        ),
        mongo_connect_timeout_ms=int(os.getenv("MONGO_CONNECT_TIMEOUT_MS", "5000")),
    )

