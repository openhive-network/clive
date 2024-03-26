from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.validation import Function, ValidationResult, Validator

if TYPE_CHECKING:
    from clive.__private.core.keys import KeyManager


class PublicKeyAliasValidator(Validator):
    ALREADY_IN_USE_FAILURE_DESCRIPTION: Final[str] = "Alias is already in use."

    def __init__(self, key_manager: KeyManager, *, validate_like_adding_new: bool = False) -> None:
        super().__init__()
        self.key_manager = key_manager
        self.validate_like_adding_new = validate_like_adding_new

    def validate(self, value: str) -> ValidationResult:
        result = self.success()

        validators = [
            Function(self._validate_is_key_alias_available, self.ALREADY_IN_USE_FAILURE_DESCRIPTION),
        ]

        return result.merge([validator.validate(value) for validator in validators])

    def _validate_is_key_alias_available(self, value: str) -> bool:
        if not self.validate_like_adding_new:
            return True
        return self.key_manager.is_public_alias_available(value)
