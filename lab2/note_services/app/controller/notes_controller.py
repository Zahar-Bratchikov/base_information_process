from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from ..schemas import CreateNoteRequest, NoteContentResponse, NoteMetaResponse, UpdateNoteRequest
from ..service.note_service import NoteService

router = APIRouter(prefix="/notes", tags=["notes"])


def get_service(request: Request) -> NoteService:
    return request.app.state.note_service


@router.post("", response_model=NoteContentResponse)
async def create_note(body: CreateNoteRequest, request: Request):
    service = get_service(request)
    row = await service.create_note(body.content, note_id=body.note_id)
    return NoteContentResponse(
        note_id=row.note_id,
        content=row.content,
        created_at=service._dt_from_ts(row.created_at_ts),
        updated_at=service._dt_from_ts(row.updated_at_ts),
        last_read_at=service._dt_from_ts(row.last_read_at_ts),
    )


@router.put("/{note_id}", response_model=NoteContentResponse)
async def update_note(note_id: str, body: UpdateNoteRequest, request: Request):
    service = get_service(request)
    row = await service.update_note(note_id, body.content)
    if row is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteContentResponse(
        note_id=row.note_id,
        content=row.content,
        created_at=service._dt_from_ts(row.created_at_ts),
        updated_at=service._dt_from_ts(row.updated_at_ts),
        last_read_at=service._dt_from_ts(row.last_read_at_ts),
    )


@router.delete("/{note_id}")
async def delete_note(note_id: str, request: Request):
    service = get_service(request)
    deleted = await service.delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"note_id": note_id, "deleted": True}


@router.get("/{note_id}/meta", response_model=NoteMetaResponse)
async def get_note_meta(note_id: str, request: Request):
    service = get_service(request)
    row = await service.get_meta(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteMetaResponse(
        note_id=row.note_id,
        created_at=service._dt_from_ts(row.created_at_ts),
        updated_at=service._dt_from_ts(row.updated_at_ts),
        last_read_at=service._dt_from_ts(row.last_read_at_ts),
    )


@router.get("/{note_id}", response_model=NoteContentResponse)
async def get_note(note_id: str, request: Request):
    service = get_service(request)
    row = await service.get_content_and_meta(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteContentResponse(
        note_id=row.note_id,
        content=row.content,
        created_at=service._dt_from_ts(row.created_at_ts),
        updated_at=service._dt_from_ts(row.updated_at_ts),
        last_read_at=service._dt_from_ts(row.last_read_at_ts),
    )

