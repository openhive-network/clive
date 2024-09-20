from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.validation import Function, ValidationResult

from clive.__private.validators.bad_account_validator import BadAccountValidator

if TYPE_CHECKING:
    from clive.__private.core.accounts.account_manager import AccountManager


class ProxyValidator(BadAccountValidator):
    PROXY_SELF_FAILURE_DESCRIPTION: Final[str] = "Cannot set proxy to yourself"

    def __init__(self, account_manager: AccountManager, *, check_is_not_working_account: bool = False) -> None:
        """
        Initialise the Validator.

        Args:
        ----
        account_manager: Used to check is account bad and retrieve working account name if needed.
        check_is_not_working_account: Set to True if e.g. setting a proxy, additional validation will take place
        """
        super().__init__(account_manager)
        self.working_account_name = account_manager.working.name if check_is_not_working_account else None

    def validate(self, value: str) -> ValidationResult:
        super_result = super().validate(value)

        validators = [
            Function(self._validate_set_proxy_to_self, self.PROXY_SELF_FAILURE_DESCRIPTION),
        ]

        return ValidationResult.merge([super_result] + [validator.validate(value) for validator in validators])

    def _validate_set_proxy_to_self(self, value: str) -> bool:
        if self.working_account_name is None:
            return True  # Validation is successful when no working account name is set

        return self.working_account_name != value
