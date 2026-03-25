from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from bson.errors import InvalidId

from ..mongo_service import MongoService
from ..schemas import (
    MovieCreateRequest,
    MovieFilterQuery,
    MovieResponse,
    MovieUpdateRequest,
    MoviesCountResponse,
    MoviesListResponse,
)


router = APIRouter()


def get_service(request: Request) -> MongoService:
    return request.app.state.mongo_service


@router.post("", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
def create_movie(body: MovieCreateRequest, request: Request):
    service = get_service(request)
    movie_id = service.insert_movie(body.model_dump())
    movie = service.get_movie(movie_id)
    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Movie was inserted but cannot be loaded",
        )
    return movie


@router.get(
    "/{movie_id}",
    response_model=MovieResponse,
    responses={404: {"description": "Movie not found"}},
)
def get_movie(movie_id: str, request: Request):
    service = get_service(request)
    try:
        movie = service.get_movie(movie_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid movie_id")
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.put(
    "/{movie_id}",
    response_model=MovieResponse,
    responses={404: {"description": "Movie not found"}},
)
def update_movie(movie_id: str, body: MovieUpdateRequest, request: Request):
    service = get_service(request)
    try:
        ok = service.update_movie(movie_id, body.model_dump())
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid movie_id")
    if not ok:
        raise HTTPException(status_code=404, detail="Movie not found")
    movie = service.get_movie(movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.delete(
    "/{movie_id}",
    responses={404: {"description": "Movie not found"}},
)
def delete_movie(movie_id: str, request: Request):
    service = get_service(request)
    try:
        deleted = service.delete_movie(movie_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid movie_id")
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"movie_id": movie_id, "deleted": deleted}


@router.get("", response_model=MoviesListResponse)
def list_movies(
    request: Request,
    filters: MovieFilterQuery = Depends(),
):
    service = get_service(request)
    items, count = service.search_and_count(filters)
    return {"count": count, "items": items}


@router.get("/count", response_model=MoviesCountResponse)
def count_movies(
    request: Request,
    filters: MovieFilterQuery = Depends(),
):
    service = get_service(request)
    count = service.count_only(filters)
    return {"count": count}

