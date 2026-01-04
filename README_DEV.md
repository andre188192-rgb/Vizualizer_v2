# README_DEV

## Запуск проекта (текущее состояние)

### Docker Compose (backend + frontend)

```bash
docker compose up --build
```

Ожидаемые сервисы:
- `backend` (FastAPI) на http://localhost:8000
- `frontend` (Vite dev server) на http://localhost:5173

### Локальный запуск (без Docker)

```bash
# backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
CNC_API_KEY=changeme CNC_BASIC_USER=admin CNC_BASIC_PASS=admin uvicorn app.main:app --reload
```

```bash
# frontend
cd frontend
npm install
VITE_API_USER=admin VITE_API_PASS=admin npm run dev
```

```bash
# desktop
cd desktop
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Какие сервисы поднимаются

- `backend`: FastAPI + SQLite, хранение телеметрии и событий.
- `frontend`: React/Vite UI для мониторинга.
- `desktop`: PyQt5 инженерный анализ логов.

## Известные ограничения/долги

- `npm install` может блокироваться сетевой политикой (HTTP 403 от registry).
- `pip install -r desktop/requirements.txt` может не установить `reportlab` при ограниченном доступе к PyPI.
- Для Windows PowerShell требуется `Activate.ps1` вместо `source`.
- `docker compose up --build` зависит от доступа к npm registry.
