from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ...core.security import require_api_key
from ...db.models import Maintenance
from ...db.session import get_session
from ...schemas.maintenance import MaintenancePayload

router = APIRouter()


@router.get("/maintenance")
async def list_maintenance(session: Session = Depends(get_session)) -> dict:
    maintenance = session.exec(select(Maintenance).order_by(Maintenance.timestamp.desc())).all()
    return {"maintenance": maintenance}


@router.post("/maintenance", dependencies=[Depends(require_api_key)])
async def add_maintenance(
    payload: MaintenancePayload,
    session: Session = Depends(get_session),
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
