from fastapi import APIRouter, HTTPException, Request
import redis

from ..redis_service import RedisService
from ..schemas import ListIncrementRequest, ListReplaceRequest, TTLUpdateRequest

router = APIRouter()


def get_service(request: Request) -> RedisService:
    return request.app.state.redis_service


@router.get("/{key}")
def get_list(key: str, request: Request):
    service = get_service(request)
    if not service.exists(key):
        raise HTTPException(status_code=404, detail="Key not found")
    values = service.list_get(key)
    return {"key": key, "values": values}


@router.put("/{key}")
def replace_list(key: str, body: ListReplaceRequest, request: Request):
    service = get_service(request)
    service.list_replace(key, body.values, ttl_seconds=body.ttl_seconds)
    return {"key": key, "values": body.values, "ttl_seconds": body.ttl_seconds}


@router.delete("/{key}")
def delete_list(key: str, request: Request):
    service = get_service(request)
    deleted = service.delete_key(key)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": key, "deleted": deleted}


@router.post("/{key}/ttl")
def set_list_ttl(key: str, body: TTLUpdateRequest, request: Request):
    service = get_service(request)
    ok = service.set_ttl(key, body.ttl_seconds)
    if not ok:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": key, "ttl_seconds": body.ttl_seconds}


@router.post("/{key}/increment")
def increment_list(key: str, body: ListIncrementRequest, request: Request):
    service = get_service(request)
    try:
        new_value = service.list_increment_by_index(key, body.index, body.delta)
    except redis.exceptions.ResponseError as e:
        msg = str(e)
        if "INDEX_OUT_OF_RANGE" in msg:
            raise HTTPException(status_code=404, detail="Index out of range")
        if "VALUE_NOT_INTEGER" in msg:
            raise HTTPException(status_code=400, detail="List element is not an integer")
        raise HTTPException(status_code=400, detail=msg)
    return {"key": key, "index": body.index, "new_value": new_value}

