from pydantic import BaseModel


class EventPayload(BaseModel):
    category: str
    message: str
    severity: str = "INFO"
