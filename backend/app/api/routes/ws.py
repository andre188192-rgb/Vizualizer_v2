from fastapi import APIRouter, WebSocket
from sqlmodel import Session, select

from ...db.models import Metric
from ...db.session import engine

router = APIRouter()


@router.websocket("/ws")
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
