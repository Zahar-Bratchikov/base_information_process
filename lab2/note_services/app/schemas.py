from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CreateNoteRequest(BaseModel):
    # Можно передать свой id, но по умолчанию создадим UUID.
    note_id: Optional[str] = None
    content: str = Field(..., min_length=1)


class UpdateNoteRequest(BaseModel):
    content: str = Field(..., min_length=1)


class NoteMetaResponse(BaseModel):
    note_id: str
    created_at: datetime
    updated_at: datetime
    last_read_at: datetime


class NoteContentResponse(BaseModel):
    note_id: str
    content: str
    created_at: datetime
    updated_at: datetime
    last_read_at: datetime

