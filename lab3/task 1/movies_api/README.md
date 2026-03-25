# Movies API (MongoDB)

Backend для приложения учёта просмотренных фильмов на MongoDB.

## Запуск через Docker Compose

1. Перейдите в папку `movies_api`:
   - `cd "lab3/task 1/movies_api"`
2. Поднимите сервисы:
   - `docker compose up --build`

API будет доступен по адресу: `http://localhost:8000`.

## Эндпоинты

### Health

- `GET /health`

### CRUD

- `POST /movies` - добавить фильм
- `GET /movies/{movie_id}` - получить фильм по `movie_id`
- `PUT /movies/{movie_id}` - обновить фильм (полностью)
- `DELETE /movies/{movie_id}` - удалить фильм
- `GET /movies` - список фильмов + фильтрация/пагинация
- `GET /movies/count` - количество фильмов по фильтрации

### Фильтрация (для `GET /movies` и `GET /movies/count`)

Можно передавать комбинации параметров:

- `year_from`, `year_to` - диапазон лет
- `min_rating` - оценка `>=`
- `actor` - фильм содержит актёра в списке `actors`
- `director` - режиссёр
- `genre` - жанр
- `status` - `watched` / `not_watched` или `просмотрено` / `нет`
- `offset` - сдвиг (для списка)
- `limit` - лимит (для списка)

