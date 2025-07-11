from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

from clive.__private.core.alarms.alarm_identifier import AlarmIdentifier
from clive.__private.core.formatters.case import underscore

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_alarms_data import AccountAlarmsData


type AnyAlarm = Alarm[Any, Any]


class Alarm[AlarmIdentifierT: AlarmIdentifier, AlarmDataT](ABC):
    """
    Alarm model to store alarm data and provide basic information about the alarm.

    How to complete handle an alarm in TUI:
        1. Create an alarm identifier class that inherits from `AlarmIdentifier` or reuse one of existing identifiers
            when easily distinguishable. Update identifiers union placed in all_identifiers.py.
        2. Implement a data class to store alarm data (it must inherit from `BaseAlarmData`).
        3. Create a model of your alarm by creating a class inheriting from `Alarm` (pass the alarm identifier and data
            in a generic way).
        4. Create a dedicated `AlarmFixDetails` and place it in `DETAILED_ALARM_FIX_DETAILS`.
        5. Place your alarm in `AlarmsStorage`.
        6. If you need to download additional data to check the presence of an alarm - put it in the
            `update_alarms_data` command.

    Attributes:
        ALARM_DESCRIPTION: A description of the alarm.
        FIX_ALARM_INFO: An information on how to fix the alarm.

    Args:
        identifier: An identifier of the alarm, which is used to distinguish alarms.
        alarm_data: Data associated with the alarm, which can be used to provide more information about the alarm.
        is_harmless: A flag indicating whether the alarm is harmless or not.
    """

    ALARM_DESCRIPTION: ClassVar[str] = ""
    FIX_ALARM_INFO: ClassVar[str] = "Override me"

    _alarm_name_class_map: ClassVar[dict[str, type[AnyAlarm]]] = {}

    def __init__(
        self,
        *,
        identifier: AlarmIdentifierT | None = None,
        alarm_data: AlarmDataT | None = None,
        is_harmless: bool = False,
    ) -> None:
        super().__init__()
        self.identifier = identifier
        self.alarm_data = alarm_data
        self.is_active = False
        self.is_harmless = is_harmless

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._alarm_name_class_map[cls.get_name()] = cls

    @classmethod
    def get_name(cls) -> str:
        return underscore(cls.__name__)

    @classmethod
    def all_alarm_classes(cls) -> list[type[AnyAlarm]]:
        return list(cls._alarm_name_class_map.values())

    @classmethod
    def get_alarm_class_by_name(cls, name: str) -> type[AnyAlarm]:
        try:
            return cls._alarm_name_class_map[name]
        except KeyError as error:
            raise AssertionError(f"Alarm class with name '{name}' does not exist.") from error

    def enable_alarm(self, identifier: AlarmIdentifierT, alarm_data: AlarmDataT) -> None:
        if identifier == self.identifier:
            if not self.has_data:
                # means we're loading the alarm from storage and we need to update the data
                self.alarm_data = alarm_data
                self.is_active = True
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

    @property
    def identifier_ensure(self) -> AlarmIdentifierT:
        assert self.identifier is not None, "You're trying to access alarm identifier that is not available."
        return self.identifier

    @property
    def has_data(self) -> bool:
        return self.alarm_data is not None

    @property
    def has_identifier(self) -> bool:
        return self.identifier is not None

    @abstractmethod
    def update_alarm_status(self, data: AccountAlarmsData) -> None:
        """
        Change alarm status based on data retrieved during `update_alarms_data`.

        Args:
            data: An instance that contains the latest data for the account.
        """

    @abstractmethod
    def get_alarm_basic_info(self) -> str:
        """Return the simplest possible information about the alarm."""
