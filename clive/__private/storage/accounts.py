from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from pydantic import ValidationError

from clive.__private.core.keys import KeyManager
from clive.__private.core.validate_schema_field import validate_schema_field
from clive.__private.storage.mock_database import NodeData
from clive.exceptions import CliveError
from clive.models.aliased import AccountName


class InvalidAccountNameError(CliveError):
    """An account name is invalid."""

    def __init__(self, value: str) -> None:
        self.value = value
        message = f"Given account name is invalid: `{value}`"
        super().__init__(message)


class AccountType(str, Enum):
    value: str

    WORKING = "working"
    WATCHED = "watched"


@dataclass
class Account:
    name: str
    data: NodeData = field(init=False, default_factory=NodeData, compare=False)

    def __post_init__(self) -> None:
        self.validate(self.name)

    def __hash__(self) -> int:
        return hash(self.name)

    @staticmethod
    def validate(name: str) -> None:
        """
        Validates the given account name.

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


@dataclass
class WorkingAccount(Account):
    keys: KeyManager = field(init=False, default_factory=KeyManager, compare=False)

    def __hash__(self) -> int:
        return super().__hash__()
