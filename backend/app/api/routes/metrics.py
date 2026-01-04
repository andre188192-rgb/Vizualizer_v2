from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ...core.security import require_api_key
from ...db.models import Event, Metric
from ...db.session import get_session
from ...schemas.metrics import MetricPayload

router = APIRouter()


@router.post("/metrics", dependencies=[Depends(require_api_key)])
async def ingest_metrics(
    payload: MetricPayload,
    session: Session = Depends(get_session),
) -> dict:
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
    return {"status": "accepted"}


@router.get("/metrics")
async def list_metrics(limit: int = 200, session: Session = Depends(get_session)) -> dict:
    metrics = session.exec(select(Metric).order_by(Metric.timestamp.desc()).limit(limit)).all()
    return {"metrics": list(reversed(metrics))}
