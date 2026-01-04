from fastapi import APIRouter, Depends
from sqlmodel import Session

from ...core.security import require_roles
from ...db.session import get_session
from ...schemas.metrics import MetricPayload
from .metrics import ingest_metrics, list_metrics

router = APIRouter()


@router.post("/api/data", dependencies=[Depends(require_roles({"ui", "desktop"}))])
async def api_ingest(
    payload: MetricPayload,
    session: Session = Depends(get_session),
) -> dict:
    return await ingest_metrics(payload=payload, session=session)


@router.get("/api/data", dependencies=[Depends(require_roles({"ui", "desktop"}))])
async def api_list(limit: int = 200, session: Session = Depends(get_session)) -> dict:
    return await list_metrics(limit=limit, session=session)
