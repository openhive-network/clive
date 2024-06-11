from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.core.formatters.case import underscore
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


class CliveAlarmError(CliveError):
    pass


class UnavailableAlarmDataAccessTryError(CliveAlarmError):
    _MESSAGE = "You are trying to access alarm data that is not available/active."

    def __init__(self) -> None:
        super().__init__(self._MESSAGE)


AlarmIdentifierT = TypeVar("AlarmIdentifierT")
AlarmDataT = TypeVar("AlarmDataT")


class BaseAlarmData(AbstractClassMessagePump):
    @abstractmethod
    def get_titled_data(self) -> dict[str, str]:
        pass


@dataclass
class Alarm(Generic[AlarmIdentifierT, AlarmDataT], AbstractClassMessagePump):
    """
    Alarm model to store alarm data and provide basic information about the alarm.

    How to complete handle an alarm in TUI:
    ---------------------------------------
    1. Select an alarm identifier - it can be any type, just pass it in a generic way to the `Alarm` model when selecting/creating.
    2. Implement a data class to store alarm data (it must inherit from `BaseAlarmData`).
    3. Create a model of your alarm by creating a class inheriting from `Alarm` (pass the alarm identifier and data in a generic way).
    4. Create a dedicated `AlarmFixDetails` and place it in `DETAILED_ALARM_FIX_DETAILS`.
    5. Place your alarm in `AlarmsStorage`.
    6. If you need to download additional data to check the presence of an alarm - put it in the `update_alarms_data` command.

    How to complete handle an alarm in CLI:
    ---------------------------------------
    Soon...
    """

    EXTENDED_ALARM_INFO: ClassVar[str] = "Override me"

    identifier: AlarmIdentifierT | None = None
    alarm_data: AlarmDataT | None = None
    is_fix_possible_using_clive: bool = False
    is_active: bool = field(default=False, compare=False)
    is_harmless: bool = field(default=False, compare=False)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Alarm):
            return False
        compare_result: bool = self.identifier == other.identifier
        return compare_result

    def get_alarm_name_pretty_format(self) -> str:
        """Returns the alarm name in pretty format e.g: `Alarm example name`."""
        return underscore(self.__class__.__name__).replace("_", " ").capitalize()

    def set_alarm_active(self, identifier: AlarmIdentifierT, alarm_data: AlarmDataT) -> None:
        self.is_active = True
        self.is_harmless = False
        self.identifier = identifier
        self.alarm_data = alarm_data

    def set_alarm_inactive(self) -> None:
        self.is_active = False
        self.is_harmless = False
        self.identifier = None
        self.alarm_data = None

    @property
    def ensure_alarm_data(self) -> AlarmDataT:
        assert self.alarm_data is not None, "You're trying to access alarm data that is not available/active."
        return self.alarm_data

    @abstractmethod
    def update_alarm_status(self, data: AccountAlarmsData) -> None:
        """Change alarm status based on data retrieved during `update_alarms_data`."""

    @abstractmethod
    def get_alarm_basic_info(self) -> str:
        """Returns the simplest possible information about the alarm."""
