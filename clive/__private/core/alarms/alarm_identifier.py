from __future__ import annotations

from abc import ABC
from datetime import datetime  # noqa: TCH003

from clive.models.base import CliveBaseModel


class AlarmIdentifier(CliveBaseModel, ABC):
    """Base class for alarm identifiers."""


class DateTimeAlarmIdentifier(AlarmIdentifier):
    value: datetime
