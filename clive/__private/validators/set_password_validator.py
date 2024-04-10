from __future__ import annotations

from typing import Final

from textual.validation import Length, ValidationResult, Validator


class SetPasswordValidator(Validator):
    MIN_LENGTH: Final[int] = 8
    MAX_LENGTH: Final[int] = 64

    def validate(self, value: str) -> ValidationResult:
        validators = [
            Length(minimum=self.MIN_LENGTH, maximum=self.MAX_LENGTH),
        ]

        return ValidationResult.merge([validator.validate(value) for validator in validators])
