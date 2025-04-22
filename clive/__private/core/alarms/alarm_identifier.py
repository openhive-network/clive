from __future__ import annotations

from abc import ABC

from clive.__private.models.schemas import HiveDateTime  # noqa: TCH001
from schemas.clive.base import CliveBaseModel


class AlarmIdentifier(CliveBaseModel, ABC):
    """Base class for alarm identifiers."""


class DateTimeAlarmIdentifier(AlarmIdentifier):
    value: HiveDateTime
