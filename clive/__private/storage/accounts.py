from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from pydantic import ValidationError

from clive.__private.core.alarms.alarms_storage import AlarmsStorage
from clive.__private.core.validate_schema_field import validate_schema_field
from clive.exceptions import CliveError
from clive.models.aliased import AccountName

if TYPE_CHECKING:
    from clive.__private.storage.mock_database import NodeData


class AccountError(CliveError):
    pass


class InvalidAccountNameError(AccountError):
    """An account name is invalid."""

    def __init__(self, value: str) -> None:
        self.value = value
        message = f"Given account name is invalid: `{value}`"
        super().__init__(message)


class AccountDataTooEarlyAccessError(AccountError):
    _MESSAGE = """
You are trying to access account data too early.
To check if your account data is available, use the `is_node_data_available` property.
"""

    def __init__(self) -> None:
        super().__init__(self._MESSAGE)


class AccountAlarmsTooEarlyAccessError(AccountError):
    _MESSAGE = """
You are trying to access account alarms too early.
To check if your account alarms are available, use the `is_account_alarms_available` property.
"""

    def __init__(self) -> None:
        super().__init__(self._MESSAGE)


class AccountType(str, Enum):
    value: str

    WORKING = "working"
    WATCHED = "watched"


@dataclass
class Account:
    name: str
    _alarms: AlarmsStorage = field(default_factory=AlarmsStorage, compare=False)
    _data: NodeData | None = field(init=False, default=None, compare=False)

    def __post_init__(self) -> None:
        self.validate(self.name)

    def __hash__(self) -> int:
        return hash(self.name)

    @property
    def data(self) -> NodeData:
        if self._data is None:
            raise AccountDataTooEarlyAccessError
        return self._data

    @property
    def alarms(self) -> AlarmsStorage:
        if not self._alarms.is_alarms_data_available:
            raise AccountDataTooEarlyAccessError
        return self._alarms

    @property
    def is_node_data_available(self) -> bool:
        return self._data is not None

    @property
    def is_alarms_data_available(self) -> bool:
        return self._alarms.is_alarms_data_available

    @staticmethod
    def validate(name: str) -> None:
        """
        Validate the given account name.

        Raises
        ------
        InvalidAccountNameError: if the given account name is invalid.
        """
        try:
            validate_schema_field(AccountName, name)
        except ValidationError as error:
            raise InvalidAccountNameError(name) from error

    @classmethod
    def is_valid(cls, name: str) -> bool:
        try:
            cls.validate(name)
        except InvalidAccountNameError:
            return False
        return True

    def _prepare_for_save(self) -> None:
        self._data = None  # do not store old data gathered from the node


@dataclass
class WorkingAccount(Account):
    def __hash__(self) -> int:
        return super().__hash__()
