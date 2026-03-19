from typing import Dict, List

from pydantic import BaseModel, Field


class TTLUpdateRequest(BaseModel):
    ttl_seconds: int = Field(..., ge=1, description="TTL в секундах (должен быть >= 1)")


class StringUpsertRequest(BaseModel):
    value: str
    ttl_seconds: int | None = Field(default=None, ge=1)


class IntegerUpsertRequest(BaseModel):
    value: int
    ttl_seconds: int | None = Field(default=None, ge=1)


class ListReplaceRequest(BaseModel):
    values: List[str] = Field(default_factory=list)
    ttl_seconds: int | None = Field(default=None, ge=1)


class ListIncrementRequest(BaseModel):
    index: int = Field(..., ge=0)
    delta: int


class HashUpsertRequest(BaseModel):
    fields: Dict[str, str]
    ttl_seconds: int | None = Field(default=None, ge=1)


class HashIncrementRequest(BaseModel):
    field: str
    delta: int


class DeltaIncrementRequest(BaseModel):
    delta: int

