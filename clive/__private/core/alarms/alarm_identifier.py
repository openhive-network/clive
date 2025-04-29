from __future__ import annotations

from clive.__private.models.schemas import CliveBaseModel, HiveDateTime


class AlarmIdentifier(CliveBaseModel):
    """Base class for alarm identifiers."""


class DateTimeAlarmIdentifier(AlarmIdentifier, tag=True):
    value: HiveDateTime
