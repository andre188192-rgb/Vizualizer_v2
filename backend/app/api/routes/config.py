from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ...core.security import require_roles
from ...db.models import Threshold
from ...db.session import get_session

router = APIRouter()


@router.get("/api/config", dependencies=[Depends(require_roles({"ui", "desktop"}))])
async def get_config(session: Session = Depends(get_session)) -> dict:
    threshold = session.exec(select(Threshold)).first()
    return {"thresholds": threshold}
