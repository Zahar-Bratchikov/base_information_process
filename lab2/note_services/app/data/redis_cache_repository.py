from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional

import redis


@dataclass(frozen=True)
class CachedMeta:
    created_at_ts: int
    updated_at_ts: int
    last_read_at_ts: int


class NoteCache:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    @staticmethod
    def _now_ts() -> int:
        return int(datetime.now(tz=timezone.utc).timestamp())

    @staticmethod
    def content_key(note_id: str) -> str:
        return f"note:{note_id}:content"

    @staticmethod
    def meta_key(note_id: str) -> str:
        return f"note:{note_id}:meta"

    def get_content(self, note_id: str) -> Optional[str]:
        raw = self.redis.get(self.content_key(note_id))
        if raw is None:
            return None
        if isinstance(raw, bytes):
            return raw.decode()
        return str(raw)

    def set_content(self, note_id: str, content: str) -> None:
        self.redis.set(self.content_key(note_id), content)

    def delete_content(self, note_id: str) -> None:
        self.redis.delete(self.content_key(note_id))

    def get_meta(self, note_id: str) -> Optional[CachedMeta]:
        raw = self.redis.hgetall(self.meta_key(note_id))
        if not raw:
            return None

        def _decode(v):
            if isinstance(v, bytes):
                return v.decode()
            return str(v)

        # Если какого-то поля нет, считаем кэш недостоверным.
        try:
            created_at_ts = int(_decode(raw.get(b"created_at_ts") or raw.get("created_at_ts")))
            updated_at_ts = int(_decode(raw.get(b"updated_at_ts") or raw.get("updated_at_ts")))
            last_read_at_ts = int(_decode(raw.get(b"last_read_at_ts") or raw.get("last_read_at_ts")))
        except Exception:
            return None
        return CachedMeta(created_at_ts=created_at_ts, updated_at_ts=updated_at_ts, last_read_at_ts=last_read_at_ts)

    def set_meta(self, note_id: str, meta: CachedMeta) -> None:
        self.redis.hset(
            self.meta_key(note_id),
            mapping={
                "created_at_ts": str(meta.created_at_ts),
                "updated_at_ts": str(meta.updated_at_ts),
                "last_read_at_ts": str(meta.last_read_at_ts),
            },
        )

    def update_last_read_at(self, note_id: str, last_read_at_ts: int) -> None:
        self.redis.hset(self.meta_key(note_id), "last_read_at_ts", str(last_read_at_ts))

    def delete_meta(self, note_id: str) -> None:
        self.redis.delete(self.meta_key(note_id))

