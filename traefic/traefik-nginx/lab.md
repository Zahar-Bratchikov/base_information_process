# Traefik -> backend (Python) вместо nginx

## Что поменялось

Traefik теперь маршрутизирует запросы на контейнер `backend`, а не на `nginx`.
Маршрут: `PathPrefix(`/backend`)`.

## Как запустить

1. Перейди в папку `traefic/traefik-nginx`
2. Выполни:
   - `docker compose up -d --build`
3. Открой:
   - `http://localhost:8080/backend`
   - или `https://localhost:8443/backend` (браузер может ругаться на самоподписанный сертификат)

## Как проверить

В браузере или через curl ты должен увидеть строку:
`hello from python`
