import os
from datetime import datetime

from fastapi import Depends, FastAPI, Header, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
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

engine = create_engine(DATABASE_URL, echo=False)

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
                    spindle_temp_warn=55.0,
                    spindle_temp_alarm=70.0,
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
            )
        )
    session.commit()
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
    )
    session.add(record)
    session.commit()
    session.refresh(record)
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
        )
    )
    session.commit()
    return {"status": "reset"}


@app.websocket("/ws")
async def websocket_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            with Session(engine) as session:
                payload = session.exec(select(Metric).order_by(Metric.timestamp.desc())).first()
            await websocket.send_json({"latest": payload.model_dump() if payload else None})
            await websocket.receive_text()
    except Exception:
        await websocket.close()
