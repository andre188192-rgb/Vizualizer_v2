from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ...core.security import require_api_key
from ...db.models import Threshold
from ...db.session import get_session
from ...schemas.thresholds import ThresholdPayload

router = APIRouter()


@router.get("/thresholds")
async def get_thresholds(session: Session = Depends(get_session)) -> dict:
    threshold = session.exec(select(Threshold)).first()
    return {"thresholds": threshold}


@router.put("/thresholds", dependencies=[Depends(require_api_key)])
async def update_thresholds(
    payload: ThresholdPayload,
    session: Session = Depends(get_session),
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
