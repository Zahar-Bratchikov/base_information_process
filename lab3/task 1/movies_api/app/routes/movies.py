from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database import get_database
from app.repository import (
    count_movies,
    create_movie,
    delete_movie,
    get_movie_by_id,
    list_movies,
    update_movie,
)
from app.schemas import (
    MovieCreate,
    MovieFilters,
    MovieResponse,
    MovieUpdate,
    WatchStatus,
)
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(prefix="/movies", tags=["movies"])


def _parse_filters(
    year_from: int | None = None,
    year_to: int | None = None,
    rating_min: float | None = None,
    actor: str | None = None,
    director: str | None = None,
    genre: str | None = None,
    status: WatchStatus | None = None,
) -> MovieFilters:
    return MovieFilters(
        year_from=year_from,
        year_to=year_to,
        rating_min=rating_min,
        actor=actor,
        director=director,
        genre=genre,
        status=status,
    )


@router.post("", response_model=MovieResponse)
async def create_movie_endpoint(
    body: MovieCreate,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> MovieResponse:
    """Добавить фильм."""
    doc = await create_movie(db, body)
    return MovieResponse(**doc)


@router.get("", response_model=list[MovieResponse])
async def list_movies_endpoint(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
    year_from: int | None = Query(None, ge=1800, le=2100, description="Год съёмки от"),
    year_to: int | None = Query(None, ge=1800, le=2100, description="Год съёмки до"),
    rating_min: float | None = Query(None, ge=0, le=10, description="Оценка от n и выше"),
    actor: str | None = Query(None, description="Актёр снимался в фильме"),
    director: str | None = Query(None, description="Режиссёр"),
    genre: str | None = Query(None, description="Жанр"),
    status: WatchStatus | None = Query(None, description="Просмотрено/нет"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[MovieResponse]:
    """Получить список фильмов с опциональной фильтрацией по критериям."""
    filters = _parse_filters(
        year_from=year_from,
        year_to=year_to,
        rating_min=rating_min,
        actor=actor,
        director=director,
        genre=genre,
        status=status,
    )
    items = await list_movies(db, filters=filters, skip=skip, limit=limit)
    return [MovieResponse(**x) for x in items]


@router.get("/count")
async def count_movies_endpoint(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
    year_from: int | None = Query(None, ge=1800, le=2100),
    year_to: int | None = Query(None, ge=1800, le=2100),
    rating_min: float | None = Query(None, ge=0, le=10),
    actor: str | None = Query(None),
    director: str | None = Query(None),
    genre: str | None = Query(None),
    status: WatchStatus | None = Query(None),
) -> dict[str, int]:
    """Подсчёт числа фильмов по тем же критериям (и их комбинациям)."""
    filters = _parse_filters(
        year_from=year_from,
        year_to=year_to,
        rating_min=rating_min,
        actor=actor,
        director=director,
        genre=genre,
        status=status,
    )
    n = await count_movies(db, filters=filters)
    return {"count": n}


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie_endpoint(
    movie_id: str,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> MovieResponse:
    """Получить фильм по id."""
    doc = await get_movie_by_id(db, movie_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    return MovieResponse(**doc)


@router.patch("/{movie_id}", response_model=MovieResponse)
async def update_movie_endpoint(
    movie_id: str,
    body: MovieUpdate,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> MovieResponse:
    """Обновить фильм."""
    doc = await update_movie(db, movie_id, body)
    if doc is None:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    return MovieResponse(**doc)


@router.delete("/{movie_id}")
async def delete_movie_endpoint(
    movie_id: str,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> dict[str, bool]:
    """Удалить фильм."""
    deleted = await delete_movie(db, movie_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    return {"deleted": True}
