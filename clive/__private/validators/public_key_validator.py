from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.validation import Validator

from clive.__private.core.keys import PublicKey

if TYPE_CHECKING:
    from textual.validation import ValidationResult


class PublicKeyValidator(Validator):
    INVALID_PUBLIC_KEY_FAILURE_DESCRIPTION: Final[str] = "Invalid public key format."

    def validate(self, value: str) -> ValidationResult:
        if PublicKey.is_valid(value):
            return self.success()
        return self.failure(self.INVALID_PUBLIC_KEY_FAILURE_DESCRIPTION, value)
