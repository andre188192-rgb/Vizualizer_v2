from pydantic import BaseModel


class ThresholdPayload(BaseModel):
    vibration_warn: float
    vibration_alarm: float
    vibration_reset: float
    spindle_temp_warn: float
    spindle_temp_alarm: float
    spindle_temp_reset: float
