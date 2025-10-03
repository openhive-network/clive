from __future__ import annotations

from typing import TYPE_CHECKING

from textual.validation import Validator

from clive.__private.validators.account_name_validator import AccountNameValidator
from clive.__private.validators.public_key_validator import PublicKeyValidator

if TYPE_CHECKING:
    from textual.validation import ValidationResult


class AuthorityEntryValidator(Validator):
    def __init__(self) -> None:
        super().__init__()
        self._account_name_validator = AccountNameValidator()
        self._public_key_validator = PublicKeyValidator()

    def validate(self, value: str) -> ValidationResult:
        if value.startswith("STM"):
            return self._public_key_validator.validate(value)
        return self._account_name_validator.validate(value)
