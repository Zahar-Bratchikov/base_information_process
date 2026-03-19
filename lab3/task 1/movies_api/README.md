# Movies API — учёт просмотренных фильмов (MongoDB)

Backend для приложения учёта просмотренных фильмов на FastAPI и MongoDB.

## Поля документа фильма

- **title** — название фильма
- **studio** — студия
- **year** — год съёмки
- **rating** — оценка (0–10)
- **status** — статус: `watched` (просмотрено) / `not_watched` (нет)
- **actors** — список актёров
- **director** — режиссёр
- **genre** — жанр

## Запуск

1. Поднять MongoDB (например, через docker-compose в этой папке):

   ```bash
   docker-compose up -d
   ```

2. Установить зависимости и запустить API:

   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. Документация: http://localhost:8000/docs

## Переменные окружения

- `APP_MONGODB_URL` — URL MongoDB (по умолчанию `mongodb://root:root@localhost:27017/`)
- `APP_MONGODB_DATABASE` — имя БД (по умолчанию `movies_db`)
- `APP_MONGODB_COLLECTION` — имя коллекции (по умолчанию `movies`)

## API

### CRUD

- `POST /movies` — добавить фильм
- `GET /movies` — список фильмов (с пагинацией `skip`, `limit`)
- `GET /movies/{movie_id}` — получить фильм по id
- `PATCH /movies/{movie_id}` — обновить фильм
- `DELETE /movies/{movie_id}` — удалить фильм

### Выборка и подсчёт

Критерии задаются query-параметрами (можно комбинировать):

- **year_from**, **year_to** — диапазон лет съёмки
- **rating_min** — оценка от n и выше
- **actor** — в фильме снимался указанный актёр
- **director** — режиссёр
- **genre** — жанр
- **status** — `watched` или `not_watched`

- `GET /movies?year_from=2000&year_to=2010&rating_min=7&...` — список с фильтрами
- `GET /movies/count?year_from=2000&rating_min=7&...` — число фильмов по тем же критериям

Примеры:

```bash
# Фильмы 2010–2020 с оценкой не ниже 8
GET /movies?year_from=2010&year_to=2020&rating_min=8

# Фильмы с участием актёра
GET /movies?actor=Leonardo DiCaprio

# Просмотренные фильмы режиссёра
GET /movies?director=Christopher Nolan&status=watched

# Количество непросмотренных фильмов жанра "драма"
GET /movies/count?genre=драма&status=not_watched
```
