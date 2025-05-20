from __future__ import annotations

from clive.__private.models.schemas import HiveDateTime, PreconfiguredBaseModel


class AlarmIdentifier(PreconfiguredBaseModel):
    """Base class for alarm identifiers."""


class DateTimeAlarmIdentifier(AlarmIdentifier, tag=True):
    value: HiveDateTime
