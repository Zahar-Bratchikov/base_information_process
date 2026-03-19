# Redis API

HTTP API к Redis (FastAPI).

## Запуск (локально)

1. Поднимите Redis (например, через Docker):
   - `docker run --rm -p 6379:6379 redis:7`
2. Запуск сервиса:
   - `pip install -r requirements.txt`
   - `uvicorn app.main:app --reload --port 8000`

Сервис использует переменные окружения:
- `REDIS_HOST` (по умолчанию `localhost`)
- `REDIS_PORT` (по умолчанию `6379`)
- `REDIS_DB` (по умолчанию `0`)
- `REDIS_PASSWORD` (необязательно)

## Эндпоинты

`/health`

### `string`
- `PUT /strings/{key}`: установить/обновить (опционально TTL)
- `GET /strings/{key}`: получить значение
- `DELETE /strings/{key}`: удалить
- `POST /strings/{key}/ttl`: установить TTL
- `POST /strings/{key}/increment`: `INCRBY`

### `integer`
- `PUT /integers/{key}`: установить/обновить (опционально TTL)
- `GET /integers/{key}`: получить число
- `DELETE /integers/{key}`: удалить
- `POST /integers/{key}/ttl`: установить TTL
- `POST /integers/{key}/increment`: `INCRBY`

### `list`
- `PUT /lists/{key}`: заменить список целиком
- `GET /lists/{key}`: получить список
- `DELETE /lists/{key}`: удалить
- `POST /lists/{key}/ttl`: установить TTL
- `POST /lists/{key}/increment`: атомарно увеличить элемент по индексу (числовой)

### `hash`
- `PUT /hashes/{key}`: установить/обновить поля
- `GET /hashes/{key}`: получить все поля
- `DELETE /hashes/{key}`: удалить
- `POST /hashes/{key}/ttl`: установить TTL
- `POST /hashes/{key}/increment`: `HINCRBY`

# Redis API

HTTP API к Redis (FastAPI).

## Запуск (локально)

1. Поднимите Redis (например, через Docker):
   - `docker run --rm -p 6379:6379 redis:7`
2. Запуск сервиса:
   - `pip install -r requirements.txt`
   - `uvicorn app.main:app --reload --port 8000`

Сервис использует переменные окружения:
- `REDIS_HOST` (по умолчанию `localhost`)
- `REDIS_PORT` (по умолчанию `6379`)
- `REDIS_DB` (по умолчанию `0`)
- `REDIS_PASSWORD` (необязательно)

## Эндпоинты

`/health`

### `string`
- `PUT /strings/{key}`: установить/обновить (опционально TTL)
- `GET /strings/{key}`: получить значение
- `DELETE /strings/{key}`: удалить
- `POST /strings/{key}/ttl`: установить TTL
- `POST /strings/{key}/increment`: `INCRBY`

### `integer`
- `PUT /integers/{key}`: установить/обновить (опционально TTL)
- `GET /integers/{key}`: получить число
- `DELETE /integers/{key}`: удалить
- `POST /integers/{key}/ttl`: установить TTL
- `POST /integers/{key}/increment`: `INCRBY`

### `list`
- `PUT /lists/{key}`: заменить список целиком
- `GET /lists/{key}`: получить список
- `DELETE /lists/{key}`: удалить
- `POST /lists/{key}/ttl`: установить TTL
- `POST /lists/{key}/increment`: атомарно увеличить элемент по индексу (числовой)

### `hash`
- `PUT /hashes/{key}`: установить/обновить поля
- `GET /hashes/{key}`: получить все поля
- `DELETE /hashes/{key}`: удалить
- `POST /hashes/{key}/ttl`: установить TTL
- `POST /hashes/{key}/increment`: `HINCRBY`

