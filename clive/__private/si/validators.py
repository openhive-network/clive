from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive.__private.si.exceptions import (
    BothArgumentsFromFileOrFromObjectPrividedError,
    InvalidAccountNameError,
    InvalidAuthorityLevelError,
    InvalidNumberOfKeyPairsError,
    InvalidPageNumberError,
    InvalidPageSizeError,
    InvalidPasswordLengthError,
    InvalidProfileNameError,
    MissingFromFileOrFromObjectError,
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


class ProfileNameValidator:
    def validate(self, value: str) -> None:
        validation_result = ProfileNameValidatorImpl().validate(value)
        if not validation_result.is_valid:
            raise InvalidProfileNameError(value, "".join(validation_result.failure_descriptions))


class SetPasswordValidator:
    def validate(self, value: str) -> None:
        validation_result = SetPasswordValidatorImpl().validate(value)
        if not validation_result.is_valid:
            raise InvalidPasswordLengthError(len(value), "".join(validation_result.failure_descriptions))


class AccountNameValidator:
    def __init__(self) -> None:
        super().__init__()

    def validate(self, value: str) -> None:
        validation_result = AccountNameValidatorImpl().validate(value)
        if not validation_result.is_valid:
            raise InvalidAccountNameError(value)


class PageNumberValidator:
    MIN_NUMBER: Final[int] = 0

    def __init__(self) -> None:
        super().__init__()

    def validate(self, value: int) -> None:
        if value < self.MIN_NUMBER:
            raise InvalidPageNumberError(value, self.MIN_NUMBER)


class PageSizeValidator:
    MIN_SIZE: Final[int] = 0

    def __init__(self) -> None:
        super().__init__()

    def validate(self, value: int) -> None:
        if value < self.MIN_SIZE:
            raise InvalidPageSizeError(value, self.MIN_SIZE)


class KeyPairsNumberValidator:
    MIN_NUMBER: Final[int] = 1

    def __init__(self) -> None:
        super().__init__()

    def validate(self, value: int) -> None:
        if value < self.MIN_NUMBER:
            raise InvalidNumberOfKeyPairsError(value)


class AuthorityLevelValidator:
    VALID_AUTHORITY_LEVELS: Final[list[str]] = ["owner", "active", "posting", "memo"]

    def __init__(self) -> None:
        super().__init__()

    def validate(self, value: str) -> None:
        if value not in self.VALID_AUTHORITY_LEVELS:
            raise InvalidAuthorityLevelError(value, self.VALID_AUTHORITY_LEVELS)


class LoadTransactionFromFileFromObjectValidator:
    def __init__(self) -> None:
        super().__init__()

    def validate(self, from_file_argument: str | Path | None, from_object_argument: Transaction | None = None) -> None:
        if from_file_argument is None and from_object_argument is None:
            raise MissingFromFileOrFromObjectError
        if from_file_argument is not None and from_object_argument is not None:
            raise BothArgumentsFromFileOrFromObjectPrividedError


class AlreadySignedModeValidator:
    def __init__(self) -> None:
        super().__init__()

    def validate(self, *, use_autosign_argument: bool | None, already_signed_mode_argument: AlreadySignedMode) -> None:
        if use_autosign_argument and already_signed_mode_argument in ["override", "multisign"]:
            raise WrongAlreadySignedModeAutoSignError


class SignedTransactionValidator:
    def __init__(self) -> None:
        super().__init__()

    def validate(self, sign_with: str | None, already_signed_mode_argument: AlreadySignedMode) -> None:
        if already_signed_mode_argument == "strict" and sign_with is not None:
            raise TransactionAlreadySignedError
