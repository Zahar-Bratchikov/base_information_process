from fastapi import APIRouter, HTTPException, Request
import redis

from ..redis_service import RedisService
from ..schemas import HashIncrementRequest, HashUpsertRequest, TTLUpdateRequest

router = APIRouter()


def get_service(request: Request) -> RedisService:
    return request.app.state.redis_service


@router.get("/{key}")
def get_hash(key: str, request: Request):
    service = get_service(request)
    if not service.exists(key):
        raise HTTPException(status_code=404, detail="Key not found")
    fields = service.hash_get_all(key)
    return {"key": key, "fields": fields}


@router.put("/{key}")
def upsert_hash(key: str, body: HashUpsertRequest, request: Request):
    service = get_service(request)
    service.hash_upsert(key, body.fields, ttl_seconds=body.ttl_seconds)
    return {"key": key, "fields": body.fields, "ttl_seconds": body.ttl_seconds}


@router.delete("/{key}")
def delete_hash(key: str, request: Request):
    service = get_service(request)
    deleted = service.delete_key(key)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": key, "deleted": deleted}


@router.post("/{key}/ttl")
def set_hash_ttl(key: str, body: TTLUpdateRequest, request: Request):
    service = get_service(request)
    ok = service.set_ttl(key, body.ttl_seconds)
    if not ok:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": key, "ttl_seconds": body.ttl_seconds}


@router.post("/{key}/increment")
def increment_hash(key: str, body: HashIncrementRequest, request: Request):
    service = get_service(request)
    try:
        new_value = service.hash_increment_field(key, body.field, body.delta)
    except redis.exceptions.ResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"key": key, "field": body.field, "new_value": new_value}

