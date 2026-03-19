from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi.concurrency import run_in_threadpool

from ..data.note_repository import NoteRepository, NoteRow
from ..data.redis_cache_repository import CachedMeta, NoteCache


class NoteService:
    def __init__(self, repo: NoteRepository, cache: NoteCache):
        self.repo = repo
        self.cache = cache

    @staticmethod
    def _dt_from_ts(ts: int) -> datetime:
        return datetime.fromtimestamp(ts, tz=timezone.utc)

    @staticmethod
    def _now_ts() -> int:
        return int(datetime.now(tz=timezone.utc).timestamp())

    async def create_note(self, content: str, note_id: Optional[str] = None) -> NoteRow:
        nid = note_id or str(uuid4())
        row = await run_in_threadpool(self.repo.create_note, nid, content)
        await run_in_threadpool(self.cache.set_content, nid, row.content)
        await run_in_threadpool(
            self.cache.set_meta,
            nid,
            CachedMeta(
                created_at_ts=row.created_at_ts,
                updated_at_ts=row.updated_at_ts,
                last_read_at_ts=row.last_read_at_ts,
            ),
        )
        return row

    async def update_note(self, note_id: str, content: str) -> Optional[NoteRow]:
        row = await run_in_threadpool(self.repo.update_note, note_id, content)
        if row is None:
            return None
        await run_in_threadpool(self.cache.set_content, note_id, row.content)
        await run_in_threadpool(
            self.cache.set_meta,
            note_id,
            CachedMeta(
                created_at_ts=row.created_at_ts,
                updated_at_ts=row.updated_at_ts,
                last_read_at_ts=row.last_read_at_ts,
            ),
        )
        return row

    async def delete_note(self, note_id: str) -> bool:
        deleted = await run_in_threadpool(self.repo.delete_note, note_id)
        if deleted:
            await run_in_threadpool(self.cache.delete_content, note_id)
            await run_in_threadpool(self.cache.delete_meta, note_id)
        return deleted

    async def get_meta(self, note_id: str) -> Optional[NoteRow]:
        # 1) Попробуем Redis-cache.
        cached = await run_in_threadpool(self.cache.get_meta, note_id)
        now_ts = self._now_ts()

        if cached is not None:
            # Обновляем last_read в БД и в кэше.
            await run_in_threadpool(self.repo.touch_last_read, note_id, now_ts)
            await run_in_threadpool(self.cache.update_last_read_at, note_id, now_ts)
            # Возвращаем мета (контент не нужен).
            return NoteRow(
                note_id=note_id,
                content="",
                created_at_ts=cached.created_at_ts,
                updated_at_ts=cached.updated_at_ts,
                last_read_at_ts=now_ts,
            )

        # 2) Cache miss => грузим из БД.
        row = await run_in_threadpool(self.repo.get_note_content_and_meta, note_id)
        if row is None:
            return None

        # Подкладываем кэш.
        await run_in_threadpool(self.cache.set_content, note_id, row.content)
        await run_in_threadpool(
            self.cache.set_meta,
            note_id,
            CachedMeta(created_at_ts=row.created_at_ts, updated_at_ts=row.updated_at_ts, last_read_at_ts=row.last_read_at_ts),
        )

        # Запоминаем чтение.
        await run_in_threadpool(self.repo.touch_last_read, note_id, now_ts)
        await run_in_threadpool(self.cache.update_last_read_at, note_id, now_ts)
        return NoteRow(
            note_id=row.note_id,
            content="",
            created_at_ts=row.created_at_ts,
            updated_at_ts=row.updated_at_ts,
            last_read_at_ts=now_ts,
        )

    async def get_content_and_meta(self, note_id: str) -> Optional[NoteRow]:
        # Если content есть в cache, то грузим мета оттуда тоже.
        content = await run_in_threadpool(self.cache.get_content, note_id)
        cached_meta = await run_in_threadpool(self.cache.get_meta, note_id)
        now_ts = self._now_ts()

        if content is not None and cached_meta is not None:
            await run_in_threadpool(self.repo.touch_last_read, note_id, now_ts)
            await run_in_threadpool(self.cache.update_last_read_at, note_id, now_ts)
            return NoteRow(note_id=note_id, content=content, created_at_ts=cached_meta.created_at_ts, updated_at_ts=cached_meta.updated_at_ts, last_read_at_ts=now_ts)

        row = await run_in_threadpool(self.repo.get_note_content_and_meta, note_id)
        if row is None:
            return None

        await run_in_threadpool(self.cache.set_content, note_id, row.content)
        await run_in_threadpool(
            self.cache.set_meta,
            note_id,
            CachedMeta(created_at_ts=row.created_at_ts, updated_at_ts=row.updated_at_ts, last_read_at_ts=row.last_read_at_ts),
        )

        await run_in_threadpool(self.repo.touch_last_read, note_id, now_ts)
        await run_in_threadpool(self.cache.update_last_read_at, note_id, now_ts)

        return NoteRow(note_id=row.note_id, content=row.content, created_at_ts=row.created_at_ts, updated_at_ts=row.updated_at_ts, last_read_at_ts=now_ts)

