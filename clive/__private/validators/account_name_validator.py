from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.validation import Validator

from clive.__private.core.validate_schema_field import is_schema_field_valid
from clive.__private.models.schemas import AccountName

if TYPE_CHECKING:
    from textual.validation import ValidationResult


class AccountNameValidator(Validator):
    INVALID_ACCOUNT_NAME_FAILURE_DESCRIPTION: Final[str] = "Invalid account name"

    def __init__(self) -> None:
        super().__init__()

    def validate(self, value: str) -> ValidationResult:
        if is_schema_field_valid(AccountName, value):
            return self.success()

        return self.failure(self.INVALID_ACCOUNT_NAME_FAILURE_DESCRIPTION, value)
