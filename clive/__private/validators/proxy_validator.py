from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.validation import Function, ValidationResult

from clive.__private.validators.bad_account_validator import BadAccountValidator

if TYPE_CHECKING:
    from clive.__private.core.accounts.account_manager import AccountManager


class ProxyValidator(BadAccountValidator):
    """
    Validator for proxy accounts.

    Attributes:
        PROXY_SELF_FAILURE_DESCRIPTION: Description of the failure when trying to set a proxy to yourself.

    Args:
        account_manager: Used to check is account bad and retrieve working account name if needed.
        check_is_not_working_account: Set to True if e.g. setting a proxy, additional validation will take place
    """

    PROXY_SELF_FAILURE_DESCRIPTION: Final[str] = "Cannot set proxy to yourself"

    def __init__(self, account_manager: AccountManager, *, check_is_not_working_account: bool = False) -> None:
        super().__init__(account_manager)
        self._check_is_not_working_account = check_is_not_working_account

    def validate(self, value: str) -> ValidationResult:
        super_result = super().validate(value)

        validators = [
            Function(self._validate_set_proxy_to_self, self.PROXY_SELF_FAILURE_DESCRIPTION),
        ]

        return ValidationResult.merge([super_result] + [validator.validate(value) for validator in validators])

    def _validate_set_proxy_to_self(self, value: str) -> bool:
        if not self._check_is_not_working_account or not self._account_manager.has_working_account:
            return True  # Validation is successful when no working check is needed

        return self._account_manager.working.name != value
