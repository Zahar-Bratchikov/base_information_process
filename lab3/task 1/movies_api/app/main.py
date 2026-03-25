from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import MongoClient

from .config import load_settings
from .mongo_service import MongoService
from .routes.movies import router as movies_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()

    client = MongoClient(
        host=settings.mongo_host,
        port=settings.mongo_port,
        serverSelectionTimeoutMS=settings.mongo_server_selection_timeout_ms,
        connectTimeoutMS=settings.mongo_connect_timeout_ms,
    )

    # Try a simple command at startup to surface obvious connectivity issues,
    # but don't make the service crash hard if Mongo isn't ready yet.
    try:
        client.admin.command("ping")
    except Exception:
        pass

    db = client[settings.mongo_db]
    app.state.mongo_service = MongoService(db, settings.mongo_collection)

    try:
        yield
    finally:
        try:
            client.close()
        except Exception:
            pass


app = FastAPI(title="Movies API (MongoDB)")
app.router.lifespan_context = lifespan


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(movies_router, prefix="/movies", tags=["movies"])

