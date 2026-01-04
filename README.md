# CNC Pulse Monitor

Комплексный проект для удаленного мониторинга состояния фрезерного станка с ЧПУ.

## Структура репозитория

- `firmware/` — прошивка ESP32 (PlatformIO).
- `backend/` — FastAPI сервер.
- `frontend/` — Web-клиент (React + Vite).
- `desktop/` — инженерное приложение (PyQt5).
- `docs/` — документация (.docx) и диаграммы.

## Быстрый старт

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Desktop

```bash
cd desktop
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Firmware

Откройте `firmware/` в PlatformIO и прошейте ESP32. Конфигурация берется из `config.json` на SD-карте.
