from __future__ import annotations

import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class NoteRow:
    note_id: str
    content: str
    created_at_ts: int
    updated_at_ts: int
    last_read_at_ts: int


class NoteRepository:
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        # Один файл БД, простая блокировка на запись.
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        return conn

    def _init_db(self) -> None:
        path = Path(self._db_path)
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                  note_id TEXT PRIMARY KEY,
                  content TEXT NOT NULL,
                  created_at_ts INTEGER NOT NULL,
                  updated_at_ts INTEGER NOT NULL,
                  last_read_at_ts INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    @staticmethod
    def _now_ts() -> int:
        return int(datetime.now(tz=timezone.utc).timestamp())

    def create_note(self, note_id: str, content: str) -> NoteRow:
        ts = self._now_ts()
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO notes (note_id, content, created_at_ts, updated_at_ts, last_read_at_ts)
                VALUES (?, ?, ?, ?, ?)
                """,
                (note_id, content, ts, ts, ts),
            )
            conn.commit()
        return NoteRow(note_id, content, ts, ts, ts)

    def update_note(self, note_id: str, content: str) -> Optional[NoteRow]:
        ts = self._now_ts()
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT note_id, content, created_at_ts, updated_at_ts, last_read_at_ts FROM notes WHERE note_id=?",
                (note_id,),
            ).fetchone()
            if row is None:
                return None
            created_at_ts = int(row[2])
            last_read_at_ts = int(row[4])

            conn.execute(
                """
                UPDATE notes
                SET content=?, updated_at_ts=?
                WHERE note_id=?
                """,
                (content, ts, note_id),
            )
            conn.commit()
        return NoteRow(note_id, content, created_at_ts, ts, last_read_at_ts)

    def delete_note(self, note_id: str) -> bool:
        with self._lock, self._connect() as conn:
            cur = conn.execute("DELETE FROM notes WHERE note_id=?", (note_id,))
            conn.commit()
            return cur.rowcount > 0

    def get_note_meta(self, note_id: str) -> Optional[NoteRow]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT note_id, content, created_at_ts, updated_at_ts, last_read_at_ts FROM notes WHERE note_id=?",
                (note_id,),
            ).fetchone()
            if row is None:
                return None
            return NoteRow(note_id=row[0], content=row[1], created_at_ts=int(row[2]), updated_at_ts=int(row[3]), last_read_at_ts=int(row[4]))

    def touch_last_read(self, note_id: str, new_last_read_ts: int) -> bool:
        with self._lock, self._connect() as conn:
            cur = conn.execute(
                "UPDATE notes SET last_read_at_ts=? WHERE note_id=?",
                (new_last_read_ts, note_id),
            )
            conn.commit()
            return cur.rowcount > 0

    def get_note_content_and_meta(self, note_id: str) -> Optional[NoteRow]:
        return self.get_note_meta(note_id)

