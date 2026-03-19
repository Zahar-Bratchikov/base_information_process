# Note Service (SQLite + Redis cache)

Сервис хранения заметок.

## Endpoints

- `POST /notes`
  - body: `{"note_id": "optional-uuid", "content": "..."}` (если `note_id` нет — сгенерируем)
- `PUT /notes/{note_id}`
  - body: `{"content":"..."}`
- `DELETE /notes/{note_id}`
- `GET /notes/{note_id}/meta`
- `GET /notes/{note_id}`

## Environment

- `REDIS_HOST` (default `localhost`)
- `REDIS_PORT` (default `6379`)
- `REDIS_DB` (default `0`)
- `REDIS_PASSWORD` (optional)
- `DB_PATH` (default `./data/notes.db`)

## Запуск

```bash
cd lab2/note_services
docker compose up --build
```

API будет доступен на `http://localhost:8001`.

