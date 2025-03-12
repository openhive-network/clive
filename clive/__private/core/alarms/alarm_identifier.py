from __future__ import annotations

from clive.__private.models.schemas import HiveDateTime  # noqa: TCH001
from schemas.clive.base import CliveBaseModel


class AlarmIdentifier(CliveBaseModel):
    """Base class for alarm identifiers."""


class DateTimeAlarmIdentifier(AlarmIdentifier, tag=True):
    value: HiveDateTime
