from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pydantic import ValidationError

from clive.__private.core.alarms.alarms_storage import AlarmsStorage
from clive.__private.core.validate_schema_field import validate_schema_field
from clive.__private.models.schemas import AccountName
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from clive.__private.core.commands.data_retrieval.update_node_data import NodeData
    from clive.__private.core.known_exchanges import ExchangeEntity


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
To check if your account alarms are available, use the `is_alarms_data_available` property.
"""

    def __init__(self) -> None:
        super().__init__(self._MESSAGE)


@dataclass
class Account:
    name: str

    def __post_init__(self) -> None:
        self.validate(self.name)

    def __hash__(self) -> int:
        return hash(self.name)

    @staticmethod
    def ensure_account_name(account: str | Account) -> str:
        return account if isinstance(account, str) else account.name

    @staticmethod
    def validate(name: str) -> None:
        """
        Validate the given account name.

        Args:
            name: The account name to validate.

        Raises:
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


@dataclass
class ExchangeAccount(Account):
    entity: ExchangeEntity
    hive_deposit: bool = True
    hbd_deposit: bool = False
    encrypted_memo: bool = False
    recurrent_transfers: bool = False

    def __hash__(self) -> int:
        return super().__hash__()


@dataclass
class TrackedAccount(Account):
    _alarms: AlarmsStorage = field(default_factory=AlarmsStorage, compare=False)
    _data: NodeData | None = field(default=None, compare=False)

    def __hash__(self) -> int:
        return super().__hash__()

    @property
    def data(self) -> NodeData:
        if self._data is None:
            raise AccountDataTooEarlyAccessError
        return self._data

    @property
    def alarms(self) -> AlarmsStorage:
        if not self._alarms.is_alarms_data_available:
            raise AccountAlarmsTooEarlyAccessError
        return self._alarms

    @property
    def is_node_data_available(self) -> bool:
        return self._data is not None

    @property
    def is_alarms_data_available(self) -> bool:
        return self._alarms.is_alarms_data_available


@dataclass
class KnownAccount(Account):
    def __hash__(self) -> int:
        return super().__hash__()


@dataclass
class WatchedAccount(TrackedAccount):
    def __hash__(self) -> int:
        return super().__hash__()

    @classmethod
    def create_from_working(cls, account: WorkingAccount) -> WatchedAccount:
        return cls(account.name, account._alarms, account._data)


@dataclass
class WorkingAccount(TrackedAccount):
    def __hash__(self) -> int:
        return super().__hash__()

    @classmethod
    def create_from_watched(cls, account: WatchedAccount) -> WorkingAccount:
        return cls(account.name, account._alarms, account._data)
