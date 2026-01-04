from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ...core.security import require_api_key
from ...db.models import Event
from ...db.session import get_session
from ...schemas.events import EventPayload

router = APIRouter()


@router.get("/events")
async def list_events(session: Session = Depends(get_session)) -> dict:
    events = session.exec(select(Event).order_by(Event.timestamp.desc())).all()
    return {"events": events}


@router.post("/events", dependencies=[Depends(require_api_key)])
async def add_event(
    payload: EventPayload,
    session: Session = Depends(get_session),
) -> dict:
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
    return {"event": record}
