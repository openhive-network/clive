from __future__ import annotations

from abc import ABC

from clive.__private.models.base import CliveBaseModel
from clive.__private.models.schemas import HiveDateTime  # noqa: TC001


class AlarmIdentifier(CliveBaseModel, ABC):
    """Base class for alarm identifiers."""


class DateTimeAlarmIdentifier(AlarmIdentifier):
    """
    Alarm identifier based on a specific date and time.

    Args:
        value: The date and time for the alarm.
    """

    value: HiveDateTime
