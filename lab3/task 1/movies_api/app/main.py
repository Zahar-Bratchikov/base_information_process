from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import close_db, init_db
from app.routes import movies_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="Movies API",
    description="Учёт просмотренных фильмов (MongoDB). CRUD и выборка по году, оценке, актёру, режиссёру, жанру, статусу.",
    lifespan=lifespan,
)
app.include_router(movies_router)
