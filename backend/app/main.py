from datetime import datetime
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .models import MetricPayload, SnapshotRequest
from .storage import store

app = FastAPI(title="CNC Pulse Monitor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MaintenancePayload(BaseModel):
    maintenance_type: str
    performed_by: str
    comment: str | None = None


class EventPayload(BaseModel):
    category: str
    message: str
    severity: str = "INFO"


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "time": datetime.utcnow()}


@app.post("/metrics")
async def ingest_metrics(payload: MetricPayload) -> dict:
    store.add_metric(payload)
    if payload.state in {"WARN", "ALARM"}:
        store.add_event(
            category="state",
            message=f"State changed to {payload.state}",
            severity=payload.state,
        )
    return {"status": "accepted"}


@app.get("/metrics")
async def list_metrics() -> dict:
    return {"metrics": list(store.metrics)}


@app.get("/events")
async def list_events() -> dict:
    return {"events": store.list_events()}


@app.post("/events")
async def add_event(payload: EventPayload) -> dict:
    record = store.add_event(payload.category, payload.message, payload.severity)
    return {"event": record}


@app.get("/maintenance")
async def list_maintenance() -> dict:
    return {"maintenance": store.list_maintenance()}


@app.post("/maintenance")
async def add_maintenance(payload: MaintenancePayload) -> dict:
    record = store.add_maintenance(
        payload.maintenance_type, payload.performed_by, payload.comment
    )
    return {"maintenance": record}


@app.post("/snapshot")
async def request_snapshot(payload: SnapshotRequest) -> dict:
    store.add_event(
        category="snapshot",
        message=f"Snapshot request for {payload.minutes} minutes",
        severity="INFO",
    )
    return {"status": "queued", "minutes": payload.minutes}


@app.post("/alarm/reset")
async def reset_alarm() -> dict:
    store.add_event(
        category="alarm",
        message="Alarm reset requested",
        severity="INFO",
    )
    return {"status": "reset"}


@app.websocket("/ws")
async def websocket_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            payload = store.metrics[-1] if store.metrics else None
            await websocket.send_json(
                {"latest": payload.dict() if payload else None}
            )
            await websocket.receive_text()
    except Exception:
        await websocket.close()
