from __future__ import annotations

from contextlib import asynccontextmanager

import redis
from fastapi import FastAPI

from .config import load_settings
from .redis_service import RedisService
from .routes.hashes import router as hashes_router
from .routes.integers import router as integers_router
from .routes.lists import router as lists_router
from .routes.strings import router as strings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()

    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password,
    )

    # Проверяем доступность Redis при старте не делаем обязательным,
    # чтобы сервис мог подняться даже если Redis пока недоступен.
    try:
        redis_client.ping()
    except redis.exceptions.ConnectionError:
        pass

    app.state.redis_service = RedisService(redis_client)
    try:
        yield
    finally:
        try:
            redis_client.close()
        except Exception:
            pass


app = FastAPI(title="Redis API")

app.router.lifespan_context = lifespan


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(strings_router, prefix="/strings", tags=["strings"])
app.include_router(integers_router, prefix="/integers", tags=["integers"])
app.include_router(lists_router, prefix="/lists", tags=["lists"])
app.include_router(hashes_router, prefix="/hashes", tags=["hashes"])

