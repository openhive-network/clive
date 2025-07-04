from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.date_utils import utc_now
from clive.__private.core.formatters.humanize import humanize_datetime, humanize_natural_time

if TYPE_CHECKING:
    from datetime import datetime, timedelta


class BaseAlarmData(ABC):
    """Base class for alarm data."""

    @abstractmethod
    def get_titled_data(self) -> dict[str, str]:
        """
        Get a title of the data.

        Returns:
            A dictionary with titles as keys and formatted data as values.
        """


@dataclass
class AlarmDataWithStartDate(BaseAlarmData):
    """
    Class representing alarm data with a start date.

    Args:
        start_date: The start date of the alarm.
        START_DATE_LABEL: The label for the start date.
    """

    START_DATE_LABEL: ClassVar[str] = "Start date"

    start_date: datetime

    @property
    def pretty_start_date(self) -> str:
        """
        Get the start date in a human-readable format.

        Returns:
            A string representing the start date in a human-readable format.
        """
        return humanize_datetime(self.start_date)

    def get_titled_data(self) -> dict[str, str]:
        """
        Get a title of the data.

        Returns:
            A dictionary with the start date label as the key and the formatted start date as the value.
        """
        return {
            self.START_DATE_LABEL: self.pretty_start_date,
        }


@dataclass
class AlarmDataWithEndDate(BaseAlarmData):
    """
    Class representing alarm data with an end date.

    Args:
        end_date: The end date of the alarm.
        END_DATE_LABEL: The label for the end date.
        TIME_LEFT_LABEL: The label for the time left until the end date.
    """

    END_DATE_LABEL: ClassVar[str] = "End date"
    TIME_LEFT_LABEL: ClassVar[str] = "Time left"

    end_date: datetime

    @property
    def pretty_end_date(self) -> str:
        """
        Get the end date in a human-readable format.

        Returns:
            A string representing the end date in a human-readable format.
        """
        return humanize_datetime(self.end_date)

    @property
    def pretty_time_left(self) -> str:
        """
        Get the time left until the end date in a human-readable format.

        Returns:
            A string representing the time left until the end date in a human-readable format.
        """
        return humanize_natural_time(-self.time_left)

    @property
    def time_left(self) -> timedelta:
        """
        Calculate the time left until the end date.

        Returns:
            A timedelta object representing the time left until the end date.
        """
        return self.end_date - utc_now()

    def get_titled_data(self) -> dict[str, str]:
        """
        Get a title of the data.

        Returns:
            A dictionary with the end date label and time left label as keys and their formatted values.
        """
        return {
            self.END_DATE_LABEL: self.pretty_end_date,
            self.TIME_LEFT_LABEL: self.pretty_time_left,
        }


class AlarmDataWithStartAndEndDate(AlarmDataWithStartDate, AlarmDataWithEndDate):
    """Class representing alarm data with both start and end dates."""

    def get_titled_data(self) -> dict[str, str]:
        """
        Get a title of the data.

        Returns:
            A dictionary with the start date, end date, and time left labels as keys and their formatted values.
        """
        return {
            self.START_DATE_LABEL: self.pretty_start_date,
            self.END_DATE_LABEL: self.pretty_end_date,
            self.TIME_LEFT_LABEL: self.pretty_time_left,
        }


class AlarmDataNeverExpiresWithoutAction(BaseAlarmData):
    """
    Class representing alarm data that never expires without action.

    Args:
        EXPIRATION_DATE_LABEL: The label for the expiration date.
    """

    EXPIRATION_DATE_LABEL: ClassVar[str] = "Expiration date"

    def get_titled_data(self) -> dict[str, str]:
        """
        Get a title of the data.

        Returns:
            A dictionary with the expiration date label as the key and a message indicating that action is required.
        """
        return {
            self.EXPIRATION_DATE_LABEL: "never (action required)",
        }
