from collections import deque
from datetime import datetime
from typing import Deque, List

from .models import EventRecord, MaintenanceRecord, MetricPayload


class InMemoryStore:
    def __init__(self) -> None:
        self.metrics: Deque[MetricPayload] = deque(maxlen=5000)
        self.events: Deque[EventRecord] = deque(maxlen=5000)
        self.maintenance: Deque[MaintenanceRecord] = deque(maxlen=2000)
        self._event_id = 1
        self._maintenance_id = 1

    def add_metric(self, payload: MetricPayload) -> None:
        self.metrics.append(payload)

    def add_event(self, category: str, message: str, severity: str) -> EventRecord:
        record = EventRecord(
            id=self._event_id,
            timestamp=datetime.utcnow(),
            category=category,
            message=message,
            severity=severity,
        )
        self._event_id += 1
        self.events.appendleft(record)
        return record

    def list_events(self) -> List[EventRecord]:
        return list(self.events)

    def add_maintenance(
        self, maintenance_type: str, performed_by: str, comment: str | None
    ) -> MaintenanceRecord:
        record = MaintenanceRecord(
            id=self._maintenance_id,
            timestamp=datetime.utcnow(),
            maintenance_type=maintenance_type,
            performed_by=performed_by,
            comment=comment,
        )
        self._maintenance_id += 1
        self.maintenance.appendleft(record)
        return record

    def list_maintenance(self) -> List[MaintenanceRecord]:
        return list(self.maintenance)


store = InMemoryStore()
