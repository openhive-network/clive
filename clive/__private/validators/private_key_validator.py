from __future__ import annotations

from textual.validation import ValidationResult, Validator

from clive.__private.core.keys import PrivateKey


class PrivateKeyValidator(Validator):
    INVALID_PRIVATE_KEY_FAILURE_DESCRIPTION: str = "Invalid private key format."

    def validate(self, value: str) -> ValidationResult:
        if PrivateKey.is_valid(value):
            return self.success()

        return self.failure(self.INVALID_PRIVATE_KEY_FAILURE_DESCRIPTION, value)
