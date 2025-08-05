from __future__ import annotations

from abc import ABC

from clive.__private.models.schemas import HiveDateTime, PreconfiguredBaseModel


class AlarmIdentifier(PreconfiguredBaseModel, ABC):
    """Base class for alarm identifiers."""


class DateTimeAlarmIdentifier(AlarmIdentifier):
    value: HiveDateTime
