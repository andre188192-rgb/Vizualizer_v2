from sqlmodel import Session, SQLModel, create_engine, select

from ..core.settings import settings
from .models import Threshold

engine = create_engine(settings.database_url, echo=False)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        existing = session.exec(select(Threshold)).first()
        if not existing:
            session.add(
                Threshold(
                    vibration_warn=0.8,
                    vibration_alarm=1.2,
                    vibration_reset=0.6,
                    spindle_temp_warn=55.0,
                    spindle_temp_alarm=70.0,
                    spindle_temp_reset=50.0,
                )
            )
            session.commit()


def get_session() -> Session:
    with Session(engine) as session:
        yield session
