from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import (
    alarm,
    api_data,
    config,
    events,
    health,
    maintenance,
    metrics,
    snapshot,
    thresholds,
    ws,
)
from .core.logging import setup_logging
from .db.session import init_db

app = FastAPI(title="CNC Pulse Monitor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    setup_logging()
    init_db()


app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(events.router)
app.include_router(maintenance.router)
app.include_router(thresholds.router)
app.include_router(snapshot.router)
app.include_router(alarm.router)
app.include_router(config.router)
app.include_router(api_data.router)
app.include_router(ws.router)
