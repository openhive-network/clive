from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Final

from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.si.exceptions import (
    BothArgumentsFromFileOrFromObjectPrividedError,
    InvalidAccountNameError,
    InvalidNumberOfKeyPairsError,
    InvalidPageNumberError,
    InvalidPageSizeError,
    InvalidProfileNameError,
    MissingFromFileOrFromObjectError,
    PasswordRequirementsNotMetError,
    TransactionAlreadySignedError,
    WrongAlreadySignedModeAutoSignError,
)
from clive.__private.validators.account_name_validator import AccountNameValidator as AccountNameValidatorImpl
from clive.__private.validators.profile_name_validator import ProfileNameValidator as ProfileNameValidatorImpl
from clive.__private.validators.set_password_validator import SetPasswordValidator as SetPasswordValidatorImpl

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.types import AlreadySignedMode
    from clive.__private.models.transaction import Transaction


class Validator(ABC):
    """
    Abstract base class for all SI validators.

    All validators must implement the validate() method which should raise
    an appropriate exception from clive.__private.si.exceptions if validation fails.

    Configuration should be passed via __init__, and validate() should accept only the value to validate.
    """

    @abstractmethod
    def validate(self, value: object) -> None:
        """
        Validate input data.

        Args:
            value: The value to validate.

        Raises:
            An appropriate exception from clive.__private.si.exceptions if validation fails.
        """
        ...


class ProfileNameValidator(Validator):
    def validate(self, value: object) -> None:
        assert isinstance(value, str)
        validation_result = ProfileNameValidatorImpl().validate(value)
        if not validation_result.is_valid:
            raise InvalidProfileNameError(value, humanize_validation_result(validation_result))


class SetPasswordValidator(Validator):
    def validate(self, value: object) -> None:
        assert isinstance(value, str)
        validation_result = SetPasswordValidatorImpl().validate(value)
        if not validation_result.is_valid:
            raise PasswordRequirementsNotMetError(humanize_validation_result(validation_result))


class AccountNameValidator(Validator):
    def validate(self, value: object) -> None:
        assert isinstance(value, str)
        validation_result = AccountNameValidatorImpl().validate(value)
        if not validation_result.is_valid:
            raise InvalidAccountNameError(value)


class PageNumberValidator(Validator):
    MIN_NUMBER: Final[int] = 0

    def validate(self, value: object) -> None:
        assert isinstance(value, int)
        if value < self.MIN_NUMBER:
            raise InvalidPageNumberError(value, self.MIN_NUMBER)


class PageSizeValidator(Validator):
    MIN_SIZE: Final[int] = 1

    def validate(self, value: object) -> None:
        assert isinstance(value, int)
        if value < self.MIN_SIZE:
            raise InvalidPageSizeError(value, self.MIN_SIZE)


class KeyPairsNumberValidator(Validator):
    MIN_NUMBER: Final[int] = 1

    def validate(self, value: object) -> None:
        assert isinstance(value, int)
        if value < self.MIN_NUMBER:
            raise InvalidNumberOfKeyPairsError(value, self.MIN_NUMBER)


class LoadTransactionFromFileFromObjectValidator(Validator):
    def __init__(self, from_file: str | Path | None, from_object: Transaction | None = None) -> None:
        self.from_file = from_file
        self.from_object = from_object

    def validate(self, value: object = None) -> None:  # noqa: ARG002
        if self.from_file is None and self.from_object is None:
            raise MissingFromFileOrFromObjectError
        if self.from_file is not None and self.from_object is not None:
            raise BothArgumentsFromFileOrFromObjectPrividedError


class AlreadySignedModeValidator(Validator):
    def __init__(self, *, use_autosign: bool | None, already_signed_mode: AlreadySignedMode) -> None:
        self.use_autosign = use_autosign
        self.already_signed_mode = already_signed_mode

    def validate(self, value: object = None) -> None:  # noqa: ARG002
        if self.use_autosign and self.already_signed_mode in ["override", "multisign"]:
            raise WrongAlreadySignedModeAutoSignError


class SignedTransactionValidator(Validator):
    def __init__(self, sign_with: str | None, already_signed_mode: AlreadySignedMode) -> None:
        self.sign_with = sign_with
        self.already_signed_mode = already_signed_mode

    def validate(self, value: object = None) -> None:  # noqa: ARG002
        if self.already_signed_mode == "strict" and self.sign_with is not None:
            raise TransactionAlreadySignedError
