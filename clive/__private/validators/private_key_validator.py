from __future__ import annotations

from textual.validation import Function, ValidationResult, Validator

from clive.__private.core.iwax import calculate_public_key
from clive.__private.core.keys import PrivateKey, PublicKey


class PrivateKeyValidator(Validator):
    INVALID_PRIVATE_KEY_FAILURE_DESCRIPTION: str = "Invalid private key format."
    PRIVATE_KEY_NOT_MATCHED_TO_PUBLIC_FAILURE_DESCRIPTION: str = "Does not match the expected public key."

    def __init__(self, public_key_to_match: str | PublicKey | None = None) -> None:
        super().__init__()
        self._public_key_to_match = public_key_to_match

    def validate(self, value: str) -> ValidationResult:
        valid_private_key_result = Function(
            self._validate_private_key, self.INVALID_PRIVATE_KEY_FAILURE_DESCRIPTION
        ).validate(value)
        validation_results = [valid_private_key_result]

        if valid_private_key_result.is_valid:
            public_key_matched_result = Function(
                self._validate_matching_keys, self.PRIVATE_KEY_NOT_MATCHED_TO_PUBLIC_FAILURE_DESCRIPTION
            ).validate(value)
            validation_results.append(public_key_matched_result)

        return ValidationResult.merge(validation_results)

    def _validate_matching_keys(self, value: str) -> bool:
        if self._public_key_to_match:
            key_to_compare = (
                self._public_key_to_match
                if isinstance(self._public_key_to_match, str)
                else self._public_key_to_match.value
            )
            return key_to_compare == calculate_public_key(value).value
        return True

    def _validate_private_key(self, value: str) -> bool:
        return PrivateKey.is_valid(value)
