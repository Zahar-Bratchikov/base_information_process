from fastapi import APIRouter, HTTPException, Request
import redis

from ..redis_service import RedisService
from ..schemas import DeltaIncrementRequest, StringUpsertRequest, TTLUpdateRequest

router = APIRouter()


def get_service(request: Request) -> RedisService:
    return request.app.state.redis_service


@router.get("/{key}")
def get_string(key: str, request: Request):
    service = get_service(request)
    value = service.get_string(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": key, "value": value}


@router.put("/{key}")
def upsert_string(key: str, body: StringUpsertRequest, request: Request):
    service = get_service(request)
    service.set_string(key, body.value, ttl_seconds=body.ttl_seconds)
    return {"key": key, "value": body.value, "ttl_seconds": body.ttl_seconds}


@router.delete("/{key}")
def delete_string(key: str, request: Request):
    service = get_service(request)
    deleted = service.delete_key(key)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": key, "deleted": deleted}


@router.post("/{key}/ttl")
def set_string_ttl(key: str, body: TTLUpdateRequest, request: Request):
    service = get_service(request)
    ok = service.set_ttl(key, body.ttl_seconds)
    if not ok:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": key, "ttl_seconds": body.ttl_seconds}


@router.post("/{key}/increment")
def increment_string(key: str, body: DeltaIncrementRequest, request: Request):
    service = get_service(request)
    try:
        new_value = service.incr_string(key, body.delta)
    except redis.exceptions.ResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"key": key, "new_value": new_value}

