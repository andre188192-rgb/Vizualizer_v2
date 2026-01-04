from pydantic import BaseModel


class MaintenancePayload(BaseModel):
    maintenance_type: str
    performed_by: str
    comment: str | None = None
