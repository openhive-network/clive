from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Final

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


class BaseValidator(ABC):
    """
    Abstract base class for all SI validators.

    All validators must implement the validate() method which should raise
    an appropriate exception from clive.__private.si.exceptions if validation fails.
    """

    @abstractmethod
    def validate(self, *args: Any, **kwargs: Any) -> None:
        """
        Validate input data.

        Raises:
            An appropriate exception from clive.__private.si.exceptions if validation fails.
        """
        ...


class ProfileNameValidator(BaseValidator):
    def validate(self, value: str) -> None:
        validation_result = ProfileNameValidatorImpl().validate(value)
        if not validation_result.is_valid:
            raise InvalidProfileNameError(value, humanize_validation_result(validation_result))


class SetPasswordValidator(BaseValidator):
    def validate(self, value: str) -> None:
        validation_result = SetPasswordValidatorImpl().validate(value)
        if not validation_result.is_valid:
            raise PasswordRequirementsNotMetError(humanize_validation_result(validation_result))


class AccountNameValidator(BaseValidator):
    def validate(self, value: str) -> None:
        validation_result = AccountNameValidatorImpl().validate(value)
        if not validation_result.is_valid:
            raise InvalidAccountNameError(value)


class PageNumberValidator(BaseValidator):
    MIN_NUMBER: Final[int] = 0

    def validate(self, value: int) -> None:
        if value < self.MIN_NUMBER:
            raise InvalidPageNumberError(value, self.MIN_NUMBER)


class PageSizeValidator(BaseValidator):
    MIN_SIZE: Final[int] = 1

    def validate(self, value: int) -> None:
        if value < self.MIN_SIZE:
            raise InvalidPageSizeError(value, self.MIN_SIZE)


class KeyPairsNumberValidator(BaseValidator):
    MIN_NUMBER: Final[int] = 1

    def validate(self, value: int) -> None:
        if value < self.MIN_NUMBER:
            raise InvalidNumberOfKeyPairsError(value, self.MIN_NUMBER)


class LoadTransactionFromFileFromObjectValidator(BaseValidator):
    def validate(self, from_file_argument: str | Path | None, from_object_argument: Transaction | None = None) -> None:
        if from_file_argument is None and from_object_argument is None:
            raise MissingFromFileOrFromObjectError
        if from_file_argument is not None and from_object_argument is not None:
            raise BothArgumentsFromFileOrFromObjectPrividedError


class AlreadySignedModeValidator(BaseValidator):
    def validate(self, *, use_autosign_argument: bool | None, already_signed_mode_argument: AlreadySignedMode) -> None:
        if use_autosign_argument and already_signed_mode_argument in ["override", "multisign"]:
            raise WrongAlreadySignedModeAutoSignError


class SignedTransactionValidator(BaseValidator):
    def validate(self, sign_with: str | None, already_signed_mode_argument: AlreadySignedMode) -> None:
        if already_signed_mode_argument == "strict" and sign_with is not None:
            raise TransactionAlreadySignedError
