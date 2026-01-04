# CNC Pulse Monitor API

## Аутентификация
- `/api/data` и `/api/config` защищены Basic Auth.
- Логин/пароль: `CNC_BASIC_USER` / `CNC_BASIC_PASS` (env).
- Остальные эндпоинты используют `X-API-Key` для записи (`CNC_API_KEY`).

## Эндпоинты

### POST /metrics
Загрузка телеметрии с ESP32. Требуется `X-API-Key`.

### GET /metrics
Получение списка метрик.

### POST /api/data
То же, что `/metrics`, но через Basic Auth.

### GET /api/data
Чтение метрик через Basic Auth.

### GET /api/config
Возвращает текущие пороги.

### PUT /thresholds
Обновление порогов. Требуется `X-API-Key`.
