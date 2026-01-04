from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session

from ...core.security import require_api_key
from ...db.models import Event
from ...db.session import get_session
from ...schemas.metrics import SnapshotRequest

router = APIRouter()


@router.post("/snapshot", dependencies=[Depends(require_api_key)])
async def request_snapshot(
    payload: SnapshotRequest,
    session: Session = Depends(get_session),
) -> dict:
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
