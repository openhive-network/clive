from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.date_utils import utc_now
from clive.__private.core.formatters.humanize import humanize_datetime, humanize_natural_time

if TYPE_CHECKING:
    from datetime import datetime, timedelta


class BaseAlarmData(ABC):
    @abstractmethod
    def get_titled_data(self) -> dict[str, str]:
        pass


@dataclass(replace=False)  # type: ignore[call-overload]
class AlarmDataWithStartDate(BaseAlarmData):
    START_DATE_LABEL: ClassVar[str] = "Start date"

    start_date: datetime

    @property
    def pretty_start_date(self) -> str:
        return humanize_datetime(self.start_date)

    def get_titled_data(self) -> dict[str, str]:
        return {
            self.START_DATE_LABEL: self.pretty_start_date,
        }


@dataclass(replace=False)  # type: ignore[call-overload]
class AlarmDataWithEndDate(BaseAlarmData):
    END_DATE_LABEL: ClassVar[str] = "End date"
    TIME_LEFT_LABEL: ClassVar[str] = "Time left"

    end_date: datetime

    @property
    def pretty_end_date(self) -> str:
        return humanize_datetime(self.end_date)

    @property
    def pretty_time_left(self) -> str:
        return humanize_natural_time(-self.time_left)

    @property
    def time_left(self) -> timedelta:
        return self.end_date - utc_now()

    def get_titled_data(self) -> dict[str, str]:
        return {
            self.END_DATE_LABEL: self.pretty_end_date,
            self.TIME_LEFT_LABEL: self.pretty_time_left,
        }


class AlarmDataWithStartAndEndDate(AlarmDataWithStartDate, AlarmDataWithEndDate):  # type: ignore[misc]
    def get_titled_data(self) -> dict[str, str]:
        return {
            self.START_DATE_LABEL: self.pretty_start_date,
            self.END_DATE_LABEL: self.pretty_end_date,
            self.TIME_LEFT_LABEL: self.pretty_time_left,
        }


class AlarmDataNeverExpiresWithoutAction(BaseAlarmData):
    EXPIRATION_DATE_LABEL: ClassVar[str] = "Expiration date"

    def get_titled_data(self) -> dict[str, str]:
        return {
            self.EXPIRATION_DATE_LABEL: "never (action required)",
        }
