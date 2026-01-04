from datetime import datetime

from sqlmodel import Field, SQLModel


class Metric(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime
    state: str
    voltage: float
    current: float
    power: float
    flow_rate: float
    spindle_temp: float
    vibration_rms: float
    vibration_x_rms: float | None = None
    vibration_y_rms: float | None = None
    vibration_z_rms: float | None = None
    motor_current: float | None = None
    ground_present: bool
    cycle_count: int


class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime
    category: str
    message: str
    severity: str
    resolved: bool = False


class Maintenance(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime
    maintenance_type: str
    performed_by: str
    comment: str | None = None


class Threshold(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    vibration_warn: float
    vibration_alarm: float
    vibration_reset: float
    spindle_temp_warn: float
    spindle_temp_alarm: float
    spindle_temp_reset: float
