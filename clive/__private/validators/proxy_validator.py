from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive.__private.validators.account_name_validator import AccountNameValidator

if TYPE_CHECKING:
    from textual.validation import ValidationResult


class ProxyValidator(AccountNameValidator):
    PROXY_SELF_FAILURE_DESCRIPTION: Final[str] = "Cannot set proxy to yourself"

    def __init__(self, working_account_name: str | None = None) -> None:
        """
        Initialise the Validator.

        Args:
        ----
        working_account_name: Set to working account name if e.g. setting a proxy, additional validation will take place
        """
        super().__init__()
        self.working_account_name = working_account_name

    def validate(self, value: str) -> ValidationResult:
        result = super().validate(value)

        if self.working_account_name is not None and self.working_account_name == value:
            result = result.merge([self.failure(self.PROXY_SELF_FAILURE_DESCRIPTION, value)])

        return result
