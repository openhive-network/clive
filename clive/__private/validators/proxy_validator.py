from __future__ import annotations

from typing import Final

from textual.validation import Function, ValidationResult

from clive.__private.validators.account_name_validator import AccountNameValidator


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
        super_result = super().validate(value)

        validators = [
            Function(self._validate_set_proxy_to_self, self.PROXY_SELF_FAILURE_DESCRIPTION),
        ]

        return ValidationResult.merge([super_result] + [validator.validate(value) for validator in validators])

    def _validate_set_proxy_to_self(self, value: str) -> bool:
        if self.working_account_name is not None and self.working_account_name == value:
            return False
        return True
