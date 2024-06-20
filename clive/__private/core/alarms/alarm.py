from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeAlias, TypeVar

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


AlarmIdentifierT = TypeVar("AlarmIdentifierT")
AlarmDataT = TypeVar("AlarmDataT")
AnyAlarm: TypeAlias = "Alarm[Any, Any]"


class BaseAlarmData(ABC):
    @abstractmethod
    def get_titled_data(self) -> dict[str, str]:
        pass


@dataclass
class Alarm(Generic[AlarmIdentifierT, AlarmDataT], ABC):
    """
    Alarm model to store alarm data and provide basic information about the alarm.

    How to complete handle an alarm in TUI:
    ---------------------------------------
    1. Select an alarm identifier - it can be any type, just pass it in a generic way to the `Alarm` model when
       selecting/creating.
    2. Implement a data class to store alarm data (it must inherit from `BaseAlarmData`).
    3. Create a model of your alarm by creating a class inheriting from `Alarm` (pass the alarm identifier and data in
       a generic way).
    4. Create a dedicated `AlarmFixDetails` and place it in `DETAILED_ALARM_FIX_DETAILS`.
    5. Place your alarm in `AlarmsStorage`.
    6. If you need to download additional data to check the presence of an alarm - put it in the `update_alarms_data`
       command.

    How to complete handle an alarm in CLI:
    ---------------------------------------
    Soon...
    """

    EXTENDED_ALARM_INFO: ClassVar[str] = "Override me"
    FIX_ALARM_INFO: ClassVar[str] = "Override me"

    identifier: AlarmIdentifierT | None = None
    alarm_data: AlarmDataT | None = None
    is_active: bool = False
    is_harmless: bool = False

    def enable_alarm(self, identifier: AlarmIdentifierT, alarm_data: AlarmDataT) -> None:
        if identifier == self.identifier:
            return

        self.is_active = True
        self.is_harmless = False
        self.identifier = identifier
        self.alarm_data = alarm_data

    def disable_alarm(self) -> None:
        self.is_active = False
        self.is_harmless = False
        self.identifier = None
        self.alarm_data = None

    @property
    def alarm_data_ensure(self) -> AlarmDataT:
        assert self.alarm_data is not None, "You're trying to access alarm data that is not available/active."
        return self.alarm_data

    @abstractmethod
    def update_alarm_status(self, data: AccountAlarmsData) -> None:
        """Change alarm status based on data retrieved during `update_alarms_data`."""

    @abstractmethod
    def get_alarm_basic_info(self) -> str:
        """Return the simplest possible information about the alarm."""
