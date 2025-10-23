from __future__ import annotations

from typing import Final

from clive.__private.models.schemas import AccountName, is_matching_model
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
    MIN_LENGTH: Final[int] = 3
    MAX_LENGTH: Final[int] = 22
    ALLOWED_SPECIAL_CHARS: Final[list[str]] = ["_", "-", ".", "@"]

    ALLOWED_LENGHT_FAILURE_DESCRIPTION: Final[str] = (
        f"""Profile name must be between {MIN_LENGTH} and {MAX_LENGTH} characters long."""
    )
    ALLOWED_CHARACTERS_FAILURE_DESCRIPTION: Final[str] = (
        f"""Only alphanumeric characters and '{ALLOWED_SPECIAL_CHARS}' are allowed."""
    )
    PROFILE_ALREADY_EXISTS_FAILURE_DESCRIPTION: Final[str] = "Profile with this name already exists."

    def validate(self, value: str) -> None:
        if len(value) < self.MIN_LENGTH or len(value) > self.MAX_LENGTH:
            raise InvalidProfileNameError(value, self.ALLOWED_LENGHT_FAILURE_DESCRIPTION)
        if not self._validate_allowed_characters(value):
            raise InvalidProfileNameError(value, self.ALLOWED_CHARACTERS_FAILURE_DESCRIPTION)
        if not self._validate_profile_already_exists(value):
            raise InvalidProfileNameError(value, self.PROFILE_ALREADY_EXISTS_FAILURE_DESCRIPTION)

    def _validate_allowed_characters(self, value: str) -> bool:
        return all(char.isalnum() or char in self.ALLOWED_SPECIAL_CHARS for char in value)

    def _validate_profile_already_exists(self, value: str) -> bool:
        from clive.__private.core.profile import Profile  # noqa: PLC0415

        return value not in Profile.list_profiles()


class SetPasswordValidator:
    MIN_LENGTH: Final[int] = 8
    MAX_LENGTH: Final[int] = 64

    def validate(self, value: str) -> None:
        if len(value) < self.MIN_LENGTH or len(value) > self.MAX_LENGTH:
            raise InvalidPasswordLengthError(self.MIN_LENGTH, self.MAX_LENGTH, len(value))


class AccountNameValidator:
    def __init__(self) -> None:
        super().__init__()

    def validate(self, value: str) -> None:
        if not is_matching_model(value, AccountName):
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
