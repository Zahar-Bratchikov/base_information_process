from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


# Статус просмотра
WatchStatus = Literal["watched", "not_watched"]


class MovieCreate(BaseModel):
    """Создание фильма."""

    title: str = Field(..., description="Название фильма")
    studio: str = Field(default="", description="Студия")
    year: int = Field(..., ge=1800, le=2100, description="Год съёмки")
    rating: float = Field(default=0.0, ge=0, le=10, description="Оценка")
    status: WatchStatus = Field(default="not_watched", description="Просмотрено/нет")
    actors: list[str] = Field(default_factory=list, description="Список актёров")
    director: str = Field(default="", description="Режиссёр")
    genre: str = Field(default="", description="Жанр")


class MovieUpdate(BaseModel):
    """Обновление фильма (все поля опциональны)."""

    title: str | None = None
    studio: str | None = None
    year: int | None = Field(None, ge=1800, le=2100)
    rating: float | None = Field(None, ge=0, le=10)
    status: WatchStatus | None = None
    actors: list[str] | None = None
    director: str | None = None
    genre: str | None = None


class MovieResponse(BaseModel):
    """Фильм в ответе API."""

    id: str
    title: str
    studio: str
    year: int
    rating: float
    status: WatchStatus
    actors: list[str]
    director: str
    genre: str

    model_config = {"from_attributes": True}


# --- Параметры выборки и подсчёта ---


class MovieFilters(BaseModel):
    """Критерии фильтрации (все опциональны, комбинации поддерживаются)."""

    year_from: int | None = Field(None, ge=1800, le=2100, description="Год съёмки от")
    year_to: int | None = Field(None, ge=1800, le=2100, description="Год съёмки до")
    rating_min: float | None = Field(None, ge=0, le=10, description="Оценка от n и выше")
    actor: str | None = Field(None, description="Актёр снимался в фильме")
    director: str | None = Field(None, description="Режиссёр")
    genre: str | None = Field(None, description="Жанр")
    status: WatchStatus | None = Field(None, description="Просмотрено/нет")
