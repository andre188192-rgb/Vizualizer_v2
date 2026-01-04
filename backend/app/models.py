from datetime import datetime
from pydantic import BaseModel, Field


class MetricPayload(BaseModel):
    timestamp: datetime
    state: str
    voltage: float
    current: float
    power: float
    flow_rate: float
    spindle_temp: float
    vibration_rms: float
    driver_current: float
    ground_present: bool
    cycle_count: int = Field(0, ge=0)


class EventPayload(BaseModel):
    category: str
    message: str
    severity: str = "INFO"


class MaintenancePayload(BaseModel):
    maintenance_type: str
    performed_by: str
    comment: str | None = None


class SnapshotRequest(BaseModel):
    minutes: int = Field(5, ge=1, le=60)


class ThresholdPayload(BaseModel):
    vibration_warn: float
    vibration_alarm: float
    spindle_temp_warn: float
    spindle_temp_alarm: float
