from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ...core.security import get_current_user
from ...db.models import Threshold
from ...db.session import get_session

router = APIRouter()


@router.get("/api/config", dependencies=[Depends(get_current_user)])
async def get_config(session: Session = Depends(get_session)) -> dict:
    threshold = session.exec(select(Threshold)).first()
    return {"thresholds": threshold}
