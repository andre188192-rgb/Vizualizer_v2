from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session

from ...core.security import require_api_key
from ...db.models import Event
from ...db.session import get_session

router = APIRouter()


@router.post("/alarm/reset", dependencies=[Depends(require_api_key)])
async def reset_alarm(
    session: Session = Depends(get_session),
) -> dict:
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
