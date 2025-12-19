from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Final

from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.py.exceptions import (
    InvalidAccountNameError,
    InvalidNumberOfKeyPairsError,
    InvalidPageNumberError,
    InvalidPageSizeError,
    InvalidProfileNameError,
    PasswordRequirementsNotMetError,
)
from clive.__private.validators.account_name_validator import AccountNameValidator as AccountNameValidatorImpl
from clive.__private.validators.profile_name_validator import ProfileNameValidator as ProfileNameValidatorImpl
from clive.__private.validators.set_password_validator import SetPasswordValidator as SetPasswordValidatorImpl


class Validator(ABC):
    """
    Abstract base class for all PY validators.

    All validators must implement the validate() method which should raise
    an appropriate exception from clive.__private.py.exceptions if validation fails.

    Configuration should be passed via __init__, and validate() should accept only the value to validate.
    """

    @abstractmethod
    def validate(self, value: object) -> None:
        """
        Validate input data.

        Args:
            value: The value to validate.

        Raises:
            An appropriate exception from clive.__private.py.exceptions if validation fails.
        """
        ...


class ProfileNameValidator(Validator):
    def validate(self, value: object) -> None:
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}: {value!r}")
        validation_result = ProfileNameValidatorImpl().validate(value)
        if not validation_result.is_valid:
            raise InvalidProfileNameError(value, humanize_validation_result(validation_result))


class SetPasswordValidator(Validator):
    def validate(self, value: object) -> None:
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}: {value!r}")
        validation_result = SetPasswordValidatorImpl().validate(value)
        if not validation_result.is_valid:
            raise PasswordRequirementsNotMetError(humanize_validation_result(validation_result))


class AccountNameValidator(Validator):
    def validate(self, value: object) -> None:
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}: {value!r}")
        validation_result = AccountNameValidatorImpl().validate(value)
        if not validation_result.is_valid:
            raise InvalidAccountNameError(value)


class PageNumberValidator(Validator):
    MIN_NUMBER: Final[int] = 0
    MAX_NUMBER: Final[int] = 100000

    def validate(self, value: object) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"Expected int, got {type(value).__name__}: {value!r}")
        if value < self.MIN_NUMBER or value > self.MAX_NUMBER:
            raise InvalidPageNumberError(value, self.MIN_NUMBER, self.MAX_NUMBER)


class PageSizeValidator(Validator):
    MIN_SIZE: Final[int] = 1
    MAX_SIZE: Final[int] = 1000

    def validate(self, value: object) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"Expected int, got {type(value).__name__}: {value!r}")
        if value < self.MIN_SIZE or value > self.MAX_SIZE:
            raise InvalidPageSizeError(value, self.MIN_SIZE, self.MAX_SIZE)


class KeyPairsNumberValidator(Validator):
    MIN_NUMBER: Final[int] = 1

    def validate(self, value: object) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"Expected int, got {type(value).__name__}: {value!r}")
        if value < self.MIN_NUMBER:
            raise InvalidNumberOfKeyPairsError(value, self.MIN_NUMBER)
