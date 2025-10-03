from __future__ import annotations

from typing import Final

from clive.__private.si.exceptions import (
    InvalidAccountNameError,
    InvalidAuthorityLevelError,
    InvalidNumberOfKeyPairsError,
    InvalidPageNumberError,
    InvalidPageSizeError,
    InvalidPasswordLengthError,
    InvalidProfileNameError,
)


class ProfileNameValidator:
    def validate(self, value: str) -> None:
        from clive.__private.validators.profile_name_validator import ProfileNameValidator

        validation_result = ProfileNameValidator().validate(value)
        if not validation_result.is_valid:
            raise InvalidProfileNameError(value, "".join(validation_result.failure_descriptions))


class SetPasswordValidator:
    def validate(self, value: str) -> None:
        from clive.__private.validators.set_password_validator import SetPasswordValidator

        validation_result = SetPasswordValidator().validate(value)
        if not validation_result.is_valid:
            raise InvalidPasswordLengthError(len(value), "".join(validation_result.failure_descriptions))


class AccountNameValidator:
    def __init__(self) -> None:
        super().__init__()

    def validate(self, value: str) -> None:
        from clive.__private.validators.account_name_validator import AccountNameValidator

        validation_result = AccountNameValidator().validate(value)
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
