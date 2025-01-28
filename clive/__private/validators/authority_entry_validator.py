from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.validation import Validator

from clive.__private.core.validate_schema_field import is_schema_field_valid
from clive.__private.models.schemas import PublicKey
from schemas.fields.basic import AccountName, PrivateKey

if TYPE_CHECKING:
    from textual.validation import ValidationResult


class AuthorityEntryValidator(Validator):
    INVALID_PUBLIC_KEY_FAILURE_DESCRIPTION: Final[str] = "Invalid public key"
    INVALID_ACCOUNT_OR_PRIVATE_KEY_DESCRIPTION: Final[str] = "Invalid account name or private key"

    def validate(self, value: str) -> ValidationResult:
        if value.startswith("STM"):
            if self._validate_public_key(value):
                return self.success()
            return self.failure(self.INVALID_PUBLIC_KEY_FAILURE_DESCRIPTION, value)
        if self._validate_account_name(value) or self._validate_private_key(value):
            return self.success()
        return self.failure(self.INVALID_ACCOUNT_OR_PRIVATE_KEY_DESCRIPTION)

    @staticmethod
    def _validate_account_name(value: str) -> bool:
        return is_schema_field_valid(AccountName, value)

    @staticmethod
    def _validate_public_key(value: str) -> bool:
        return is_schema_field_valid(PublicKey, value)

    @staticmethod
    def _validate_private_key(value: str) -> bool:
        return is_schema_field_valid(PrivateKey, value)
