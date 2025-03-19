from __future__ import annotations

from schemas.clive.base import CliveBaseModel
from clive.__private.models.schemas import HiveDateTime  # noqa: TCH001


class AlarmIdentifier(CliveBaseModel):
    """Base class for alarm identifiers."""


class DateTimeAlarmIdentifier(AlarmIdentifier, tag=True):
    value: HiveDateTime
