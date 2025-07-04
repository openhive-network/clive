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
    ---------------------------------------
    1. Create an alarm identifier class that inherits from `AlarmIdentifier` or reuse one of existing identifiers when
       easily distinguishable. Update identifiers union placed in all_identifiers.py.
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
        """
        Initialize an alarm with an identifier and data.

        Args:
            identifier: An instance of `AlarmIdentifier` that uniquely identifies the alarm.
            alarm_data: An instance of the data class that holds information about the alarm.
            is_harmless: A boolean indicating whether the alarm is harmless (default is False).

        Returns:
            None
        """
        super().__init__()
        self.identifier = identifier
        self.alarm_data = alarm_data
        self.is_active = False
        self.is_harmless = is_harmless

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Register the subclass in the `_alarm_name_class_map` when a class is subclassed.

        Args:
            kwargs: Additional keyword arguments passed to the superclass initializer

        Returns:
            None
        """
        super().__init_subclass__(**kwargs)
        cls._alarm_name_class_map[cls.get_name()] = cls

    @classmethod
    def get_name(cls) -> str:
        """
        Get the name of the alarm class in snake_case format.

        Returns:
            str: The name of the alarm class.
        """
        return underscore(cls.__name__)

    @classmethod
    def all_alarm_classes(cls) -> list[type[AnyAlarm]]:
        """
        Get a list of all registered alarm classes.

        Returns:
            list: A list of all alarm classes.
        """
        return list(cls._alarm_name_class_map.values())

    @classmethod
    def get_alarm_class_by_name(cls, name: str) -> type[AnyAlarm]:
        """
        Get an alarm class by its name.

        Args:
            name: The name of the alarm class in snake_case format.

        Raises:
            AssertionError: If the alarm class with the given name does not exist.

        Returns:
            type: The alarm class corresponding to the given name.
        """
        try:
            return cls._alarm_name_class_map[name]
        except KeyError as error:
            raise AssertionError(f"Alarm class with name '{name}' does not exist.") from error

    def enable_alarm(self, identifier: AlarmIdentifierT, alarm_data: AlarmDataT) -> None:
        """
        Enable the alarm with the given identifier and data.

        Args:
            identifier: An instance of `AlarmIdentifier` that uniquely identifies the alarm.
            alarm_data: An instance of the data class that holds information about the alarm.

        Returns:
            None
        """
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
        """
        Disable the alarm by resetting its state.

        Returns:
            None
        """
        self.is_active = False
        self.is_harmless = False
        self.identifier = None
        self.alarm_data = None

    @property
    def alarm_data_ensure(self) -> AlarmDataT:
        """
        Ensure that alarm data is available and return it.

        Raises:
            AssertionError: If alarm data is not available or active.

        Returns:
            AlarmDataT: The data associated with the alarm.
        """
        assert self.alarm_data is not None, "You're trying to access alarm data that is not available/active."
        return self.alarm_data

    @property
    def identifier_ensure(self) -> AlarmIdentifierT:
        """
        Ensure that the alarm identifier is available and return it.

        Raises:
            AssertionError: If the alarm identifier is not available.

        Returns:
            AlarmIdentifierT: The identifier of the alarm.
        """
        assert self.identifier is not None, "You're trying to access alarm identifier that is not available."
        return self.identifier

    @property
    def has_data(self) -> bool:
        """
        Check if the alarm has associated data.

        Returns:
            bool: True if the alarm has data, False otherwise.
        """
        return self.alarm_data is not None

    @property
    def has_identifier(self) -> bool:
        """
        Check if the alarm has an identifier.

        Returns:
            bool: True if the alarm has an identifier, False otherwise.
        """
        return self.identifier is not None

    @abstractmethod
    def update_alarm_status(self, data: AccountAlarmsData) -> None:
        """
        Change alarm status based on data retrieved during `update_alarms_data`.

        Args:
            data: An instance of `AccountAlarmsData` containing the latest data for the alarm.

        Returns:
            None
        """

    @abstractmethod
    def get_alarm_basic_info(self) -> str:
        """
        Return the simplest possible information about the alarm.

        Returns:
            str: A string containing basic information about the alarm.
        """
