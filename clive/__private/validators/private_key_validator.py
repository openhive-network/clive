from __future__ import annotations

from textual.validation import ValidationResult, Validator

from clive.__private.core.iwax import calculate_public_key
from clive.__private.core.keys import PrivateKey, PublicKey


class PrivateKeyValidator(Validator):
    INVALID_PRIVATE_KEY_FAILURE_DESCRIPTION: str = "Invalid private key format."
    PRIVATE_KEY_NOT_MATCHED_TO_PUBLIC_FAILURE_DESCRIPTION: str = "Does not match the expected public key."

    def __init__(self, public_key_to_match: str | PublicKey | None = None) -> None:
        super().__init__()
        self._public_key_to_match = public_key_to_match

    def validate(self, value: str) -> ValidationResult:
        if PrivateKey.is_valid(value):
            if self._public_key_to_match:
                self._public_key_to_match = (
                    self._public_key_to_match
                    if isinstance(self._public_key_to_match, str)
                    else self._public_key_to_match.value
                )
                if self._public_key_to_match == calculate_public_key(value).value:
                    return self.success()
                return self.failure(self.PRIVATE_KEY_NOT_MATCHED_TO_PUBLIC_FAILURE_DESCRIPTION)
            return self.success()

        return self.failure(self.INVALID_PRIVATE_KEY_FAILURE_DESCRIPTION, value)
