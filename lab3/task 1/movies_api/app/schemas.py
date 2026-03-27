from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MovieStatus(str, Enum):
    watched = "watched"
    not_watched = "not_watched"


_STATUS_ALIASES: Dict[str, MovieStatus] = {
    "watched": MovieStatus.watched,
    "просмотрено": MovieStatus.watched,
    "yes": MovieStatus.watched,
    "true": MovieStatus.watched,
    "1": MovieStatus.watched,
    "да": MovieStatus.watched,
    "not_watched": MovieStatus.not_watched,
    "нет": MovieStatus.not_watched,
    "no": MovieStatus.not_watched,
    "false": MovieStatus.not_watched,
    "0": MovieStatus.not_watched,
    "not watched": MovieStatus.not_watched,
    "не просмотрено": MovieStatus.not_watched,
}


def _parse_status(value: Any) -> MovieStatus:
    if value is None:
        raise ValueError("status is required")
    if isinstance(value, MovieStatus):
        return value

    s = str(value).strip().lower()
    s = s.replace("_", " ")
    s = " ".join(s.split())
    # Normalize for keys like "watched" and "not watched".
    normalized = s.replace(" ", "_")
    if normalized in _STATUS_ALIASES:
        return _STATUS_ALIASES[normalized]
    if s in _STATUS_ALIASES:
        return _STATUS_ALIASES[s]
    # Try also direct match with Enum value.
    if s in (MovieStatus.watched.value, MovieStatus.not_watched.value):
        return MovieStatus(s)
    raise ValueError(
        "Unknown status. Allowed: watched/not_watched или просмотрено/нет."
    )


class MovieBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    title: str = Field(..., min_length=1)
    studio: str = Field(..., min_length=1)
    year: int = Field(..., ge=0, le=3000)
    rating: float = Field(..., ge=0)
    status: MovieStatus
    actors: List[str] = Field(default_factory=list)
    director: str = Field(..., min_length=1)
    genre: str = Field(..., min_length=1)

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v: Any) -> MovieStatus:
        return _parse_status(v)

    @field_validator("actors", mode="before")
    @classmethod
    def validate_actors(cls, v: Any) -> List[str]:
        if v is None:
            return []
        if not isinstance(v, list):
            raise ValueError("actors must be a list of strings")
        cleaned: List[str] = []
        for item in v:
            s = str(item).strip()
            if s:
                cleaned.append(s)
        # Keep order but remove duplicates.
        seen = set()
        result: List[str] = []
        for name in cleaned:
            key = name.lower()
            if key not in seen:
                seen.add(key)
                result.append(name)
        return result


class MovieCreateRequest(MovieBase):
    pass


class MovieUpdateRequest(MovieBase):
    pass


class MovieResponse(BaseModel):
    id: str
    title: str
    studio: str
    year: int
    rating: float
    status: MovieStatus
    actors: List[str]
    director: str
    genre: str


class MovieFilterQuery(BaseModel):
    year_from: int | None = Field(default=None, ge=0, le=3000)
    year_to: int | None = Field(default=None, ge=0, le=3000)
    min_rating: float | None = Field(default=None, ge=0)
    actor: str | None = Field(default=None, min_length=1)
    director: str | None = Field(default=None, min_length=1)
    genre: str | None = Field(default=None, min_length=1)
    status: MovieStatus | None = None

    offset: int = Field(default=0, ge=0, description="Смещение для списка")
    limit: int = Field(default=50, ge=1, le=200, description="Лимит для списка")

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v: Any) -> MovieStatus | None:
        if v is None or v == "":
            return None
        return _parse_status(v)


class MoviesListResponse(BaseModel):
    count: int
    items: List[MovieResponse]


class MoviesCountResponse(BaseModel):
    count: int

