from __future__ import annotations

from contextlib import asynccontextmanager

import redis
from fastapi import FastAPI

from .config import load_settings
from .controller.notes_controller import router as notes_router
from .data.note_repository import NoteRepository
from .data.redis_cache_repository import NoteCache
from .service.note_service import NoteService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()

    # SQLite репозиторий.
    repo = NoteRepository(settings.db_path)

    # Redis кэш.
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password,
    )

    app.state.note_repo = repo
    app.state.note_cache = NoteCache(redis_client)
    app.state.note_service = NoteService(repo=repo, cache=app.state.note_cache)

    try:
        yield
    finally:
        try:
            redis_client.close()
        except Exception:
            pass


app = FastAPI(title="Notes Service")
app.router.lifespan_context = lifespan


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(notes_router)

