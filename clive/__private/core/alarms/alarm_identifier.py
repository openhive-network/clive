from __future__ import annotations

from abc import ABC

from clive.__private.models.base import CliveBaseModel
from clive.__private.models.schemas import HiveDateTime  # noqa: TC001


class AlarmIdentifier(CliveBaseModel, ABC):
    """Base class for alarm identifiers."""


class DateTimeAlarmIdentifier(AlarmIdentifier):
    value: HiveDateTime
