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
    """Class for errors related to accounts."""


class InvalidAccountNameError(AccountError):
    """An account name is invalid."""

    def __init__(self, value: str) -> None:
        """
        Initialize the InvalidAccountNameError with the given value.

        Args:
            value: The invalid account name.

        Returns:
            None
        """
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
        """
        Initialize the AccountAlarmsTooEarlyAccessError with a message.

        Returns:
            None
        """
        super().__init__(self._MESSAGE)


@dataclass
class Account:
    """
    Base class for accounts.

    Args:
        name: The name of the account.
    """

    name: str

    def __post_init__(self) -> None:
        """
        Post-initialization method to validate the account name.

        Returns:
            None
        """
        self.validate(self.name)

    def __hash__(self) -> int:
        """
        Return a hash of the account name.

        Returns:
            int: Hash of the account name.
        """
        return hash(self.name)

    @staticmethod
    def ensure_account_name(account: str | Account) -> str:
        """
        Ensure that the given account is a string and return its name.

        Args:
            account: The account to ensure is a string or an Account instance.

        Returns:
            str: The name of the account if it is an Account instance, or the account itself if it is a string.
        """
        return account if isinstance(account, str) else account.name

    @staticmethod
    def validate(name: str) -> None:
        """
        Validate the given account name.

        Args:
            name: The name of the account to validate.

        Raises:
            InvalidAccountNameError: if the given account name is invalid.

        Returns:
            None
        """
        try:
            validate_schema_field(AccountName, name)
        except ValidationError as error:
            raise InvalidAccountNameError(name) from error

    @classmethod
    def is_valid(cls, name: str) -> bool:
        """
        Check if the given account name is valid.

        Args:
            name: The name of the account to check.

        Raises:
            InvalidAccountNameError: if the given account name is invalid.

        Returns:
            bool: True if the account name is valid, False otherwise.
        """
        try:
            cls.validate(name)
        except InvalidAccountNameError:
            return False
        return True


@dataclass
class ExchangeAccount(Account):
    """
    Class representing an exchange account.

    Args:
        entity: The exchange entity associated with the account.
        hive_deposit: Whether the account supports Hive deposits (default: True).
        hbd_deposit: Whether the account supports HBD deposits (default: False).
        encrypted_memo: Whether the account supports encrypted memos (default: False).
        recurrent_transfers: Whether the account supports recurrent transfers (default: False).
    """

    entity: ExchangeEntity
    hive_deposit: bool = True
    hbd_deposit: bool = False
    encrypted_memo: bool = False
    recurrent_transfers: bool = False

    def __hash__(self) -> int:
        """
        Return a hash of the account name.

        Returns:
            int: Hash of the account name.
        """
        return super().__hash__()


@dataclass
class TrackedAccount(Account):
    """Base class for accounts that are tracked."""

    _alarms: AlarmsStorage = field(default_factory=AlarmsStorage, compare=False)
    _data: NodeData | None = field(default=None, compare=False)

    def __hash__(self) -> int:
        """
        Return a hash of the account name.

        Returns:
            int: Hash of the account name.
        """
        return super().__hash__()

    @property
    def data(self) -> NodeData:
        """
        Get the account data.

        Raises:
            AccountDataTooEarlyAccessError: if the account data is not available yet.

        Returns:
            NodeData: The account data.
        """
        if self._data is None:
            raise AccountDataTooEarlyAccessError
        return self._data

    @property
    def alarms(self) -> AlarmsStorage:
        """
        Get the account alarms.

        Raises:
            AccountAlarmsTooEarlyAccessError: if the account alarms are not available yet.

        Returns:
            AlarmsStorage: The account alarms.
        """
        if not self._alarms.is_alarms_data_available:
            raise AccountAlarmsTooEarlyAccessError
        return self._alarms

    @property
    def is_node_data_available(self) -> bool:
        """
        Check if the account data is available.

        Returns:
            bool: True if the account data is available, False otherwise.
        """
        return self._data is not None

    @property
    def is_alarms_data_available(self) -> bool:
        """
        Check if the account alarms data is available.

        Returns:
            bool: True if the account alarms data is available, False otherwise.
        """
        return self._alarms.is_alarms_data_available


@dataclass
class KnownAccount(Account):
    """Class representing a known account."""

    def __hash__(self) -> int:
        """
        Return a hash of the account name.

        Returns:
            int: Hash of the account name.
        """
        return super().__hash__()


@dataclass
class WatchedAccount(TrackedAccount):
    """Class representing a watched account."""

    def __hash__(self) -> int:
        """
        Return a hash of the account name.

        Returns:
            int: Hash of the account name.
        """
        return super().__hash__()

    @classmethod
    def create_from_working(cls, account: WorkingAccount) -> WatchedAccount:
        """
        Create a WatchedAccount from a WorkingAccount.

        Args:
            cls: The class itself, used for creating a new instance.
            account: The WorkingAccount to create the WatchedAccount from.

        Returns:
            WatchedAccount: A new WatchedAccount instance with the same name, alarms, and data as the WorkingAccount.
        """
        return cls(account.name, account._alarms, account._data)


@dataclass
class WorkingAccount(TrackedAccount):
    """Class representing a working account."""

    def __hash__(self) -> int:
        """
        Return a hash of the account name.

        Returns:
            int: Hash of the account name.
        """
        return super().__hash__()

    @classmethod
    def create_from_watched(cls, account: WatchedAccount) -> WorkingAccount:
        """
        Create a WorkingAccount from a WatchedAccount.

        Args:
            cls: The class itself, used for creating a new instance.
            account: The WatchedAccount to create the WorkingAccount from.

        Returns:
            WorkingAccount: A new WorkingAccount instance with the same name, alarms, and data as the WatchedAccount.
        """
        return cls(account.name, account._alarms, account._data)
