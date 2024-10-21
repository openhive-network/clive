from __future__ import annotations

from typing import Final

from textual.validation import Function, Length, ValidationResult, Validator


class ProfileNameValidator(Validator):
    MIN_LENGTH: Final[int] = 3
    MAX_LENGTH: Final[int] = 22
    ALLOWED_SPECIAL_CHARS: Final[list[str]] = ["_", "-", ".", "@"]

    ALLOWED_CHARACTERS_FAILURE_DESCRIPTION: Final[str] = (
        f"""Only alphanumeric characters and '{ALLOWED_SPECIAL_CHARS}' are allowed."""
    )
    PROFILE_ALREADY_EXISTS_FAILURE_DESCRIPTION: Final[str] = "Profile with this name already exists."

    def validate(self, value: str) -> ValidationResult:
        validators = [
            Length(minimum=self.MIN_LENGTH, maximum=self.MAX_LENGTH),
            Function(self._validate_allowed_characters, self.ALLOWED_CHARACTERS_FAILURE_DESCRIPTION),
            Function(self._validate_profile_already_exists, self.PROFILE_ALREADY_EXISTS_FAILURE_DESCRIPTION),
        ]

        return ValidationResult.merge([validator.validate(value) for validator in validators])

    def _validate_allowed_characters(self, value: str) -> bool:
        return all(char.isalnum() or char in self.ALLOWED_SPECIAL_CHARS for char in value)

    def _validate_profile_already_exists(self, value: str) -> bool:
        from clive.__private.core.profile import Profile

        return value not in Profile.list_profiles()
