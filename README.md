# CNC Pulse Monitor

Комплексный проект для удаленного мониторинга состояния фрезерного станка с ЧПУ.

## Структура репозитория

- `firmware/` — прошивка ESP32 (PlatformIO).
- `backend/` — FastAPI сервер с SQLite (можно заменить на PostgreSQL).
- `frontend/` — Web-клиент (React + Vite).
- `desktop/` — инженерное приложение (PyQt5).
- `docs/` — документация (Markdown) и диаграммы.
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
CNC_API_KEY=changeme CNC_BASIC_USER=admin CNC_BASIC_PASS=admin uvicorn app.main:app --reload
```

Для Windows (PowerShell):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:CNC_API_KEY="changeme"
$env:CNC_BASIC_USER="admin"
$env:CNC_BASIC_PASS="admin"
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
VITE_API_USER=admin VITE_API_PASS=admin npm run dev
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

Для Windows (PowerShell):

```powershell
cd desktop
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Если `pip` пытается собрать NumPy из исходников, используйте Python 3.11 (x64) или установите Microsoft C++ Build Tools.

### Firmware

Откройте `firmware/` в PlatformIO и прошейте ESP32. Конфигурация берется из `config.json` на SD-карте.
