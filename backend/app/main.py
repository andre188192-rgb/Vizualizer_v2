import os
import secrets
from datetime import datetime

from fastapi import Depends, FastAPI, Header, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import Session, SQLModel, create_engine, select

from .db import Event, Maintenance, Metric, Threshold
from .models import (
    EventPayload,
    MaintenancePayload,
    MetricPayload,
    SnapshotRequest,
    ThresholdPayload,
)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cnc_pulse.db")
API_KEY = os.getenv("CNC_API_KEY", "changeme")
BASIC_USER = os.getenv("CNC_BASIC_USER", "admin")
BASIC_PASS = os.getenv("CNC_BASIC_PASS", "admin")

engine = create_engine(DATABASE_URL, echo=False)
security = HTTPBasic()
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


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        existing = session.exec(select(Threshold)).first()
        if not existing:
            session.add(
                Threshold(
                    vibration_warn=0.8,
                    vibration_alarm=1.2,
                    vibration_reset=0.6,
                    spindle_temp_warn=55.0,
                    spindle_temp_alarm=70.0,
                    spindle_temp_reset=50.0,
                )
            )
            session.commit()


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def get_session() -> Session:
    with Session(engine) as session:
        yield session


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    is_user = secrets.compare_digest(credentials.username, BASIC_USER)
    is_pass = secrets.compare_digest(credentials.password, BASIC_PASS)
    if not (is_user and is_pass):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials.username
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


@app.post("/metrics", dependencies=[Depends(require_api_key)])
async def ingest_metrics(payload: MetricPayload, session: Session = Depends(get_session)) -> dict:
    metric = Metric(**payload.model_dump())
    session.add(metric)
    if payload.state in {"WARN", "ALARM"}:
        session.add(
            Event(
                timestamp=datetime.utcnow(),
                category="state",
                message=f"State changed to {payload.state}",
                severity=payload.state,
                resolved=False,
            )
        )
    session.commit()
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
async def list_metrics(limit: int = 200, session: Session = Depends(get_session)) -> dict:
    metrics = session.exec(select(Metric).order_by(Metric.timestamp.desc()).limit(limit)).all()
    return {"metrics": list(reversed(metrics))}


@app.get("/events")
async def list_events(session: Session = Depends(get_session)) -> dict:
    events = session.exec(select(Event).order_by(Event.timestamp.desc())).all()
    return {"events": events}


@app.post("/events", dependencies=[Depends(require_api_key)])
async def add_event(payload: EventPayload, session: Session = Depends(get_session)) -> dict:
    record = Event(
        timestamp=datetime.utcnow(),
        category=payload.category,
        message=payload.message,
        severity=payload.severity,
        resolved=False,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
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
async def list_maintenance(session: Session = Depends(get_session)) -> dict:
    maintenance = session.exec(select(Maintenance).order_by(Maintenance.timestamp.desc())).all()
    return {"maintenance": maintenance}


@app.post("/maintenance", dependencies=[Depends(require_api_key)])
async def add_maintenance(
    payload: MaintenancePayload, session: Session = Depends(get_session)
) -> dict:
    record = Maintenance(
        timestamp=datetime.utcnow(),
        maintenance_type=payload.maintenance_type,
        performed_by=payload.performed_by,
        comment=payload.comment,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return {"maintenance": record}


@app.get("/thresholds")
async def get_thresholds(session: Session = Depends(get_session)) -> dict:
    threshold = session.exec(select(Threshold)).first()
    return {"thresholds": threshold}


@app.put("/thresholds", dependencies=[Depends(require_api_key)])
async def update_thresholds(
    payload: ThresholdPayload, session: Session = Depends(get_session)
) -> dict:
    threshold = session.exec(select(Threshold)).first()
    if not threshold:
        threshold = Threshold(**payload.model_dump())
        session.add(threshold)
    else:
        for key, value in payload.model_dump().items():
            setattr(threshold, key, value)
    session.commit()
    return {"thresholds": threshold}


@app.post("/snapshot", dependencies=[Depends(require_api_key)])
async def request_snapshot(payload: SnapshotRequest, session: Session = Depends(get_session)) -> dict:
    session.add(
        Event(
            timestamp=datetime.utcnow(),
            category="snapshot",
            message=f"Snapshot request for {payload.minutes} minutes",
            severity="INFO",
            resolved=False,
        )
    )
    session.commit()
    return {"status": "queued", "minutes": payload.minutes}


@app.post("/alarm/reset", dependencies=[Depends(require_api_key)])
async def reset_alarm(session: Session = Depends(get_session)) -> dict:
    session.add(
        Event(
            timestamp=datetime.utcnow(),
            category="alarm",
            message="Alarm reset requested",
            severity="INFO",
            resolved=False,
        )
    )
    session.commit()
    return {"status": "reset"}


@app.get("/api/config", dependencies=[Depends(get_current_user)])
async def get_config(session: Session = Depends(get_session)) -> dict:
    threshold = session.exec(select(Threshold)).first()
    return {"thresholds": threshold}


@app.post("/api/data", dependencies=[Depends(get_current_user)])
async def api_ingest(payload: MetricPayload, session: Session = Depends(get_session)) -> dict:
    return await ingest_metrics(payload, session)


@app.get("/api/data", dependencies=[Depends(get_current_user)])
async def api_list(limit: int = 200, session: Session = Depends(get_session)) -> dict:
    return await list_metrics(limit, session)


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
            with Session(engine) as session:
                payload = session.exec(select(Metric).order_by(Metric.timestamp.desc())).first()
            await websocket.send_json({"latest": payload.model_dump() if payload else None})
            payload = store.metrics[-1] if store.metrics else None
            await websocket.send_json(
                {"latest": payload.dict() if payload else None}
            )
            await websocket.receive_text()
    except Exception:
        await websocket.close()
