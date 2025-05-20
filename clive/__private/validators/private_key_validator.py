from __future__ import annotations

from textual.validation import Function, ValidationResult, Validator

from clive.__private.core.iwax import calculate_public_key
from clive.__private.core.keys import PrivateKey, PublicKey


class PrivateKeyValidator(Validator):
    INVALID_PRIVATE_KEY_FAILURE_DESCRIPTION: str = "Invalid private key format."
    PRIVATE_KEY_NOT_MATCHED_TO_PUBLIC_FAILURE_DESCRIPTION: str = "Does not match the expected public key."

    def __init__(self, public_key_to_match: PublicKey | None = None) -> None:
        super().__init__()
        self._public_key_to_match = public_key_to_match

    def validate(self, value: str) -> ValidationResult:
        validators = [
            Function(self._validate_private_key, self.INVALID_PRIVATE_KEY_FAILURE_DESCRIPTION),
            Function(self._validate_matching_key, self.PRIVATE_KEY_NOT_MATCHED_TO_PUBLIC_FAILURE_DESCRIPTION),
        ]
        return ValidationResult.merge([validator.validate(value) for validator in validators])

    def _validate_matching_key(self, value: str) -> bool:
        if not self._public_key_to_match:
            return True
        if not PrivateKey.is_valid(value):
            return False
        return self._public_key_to_match == calculate_public_key(value)

    def _validate_private_key(self, value: str) -> bool:
        return PrivateKey.is_valid(value)
