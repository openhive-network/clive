from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.validation import Function, ValidationResult

from clive.__private.validators.account_name_validator import AccountNameValidator

if TYPE_CHECKING:
    from clive.__private.core.accounts.account_manager import AccountManager


class BadAccountValidator(AccountNameValidator):
    BAD_ACCOUNT_IN_INPUT_FAILURE_DESCRIPTION: Final[str] = "This account is considered as bad!"

    def __init__(self, account_manager: AccountManager, *, known_overrides_bad: bool = True) -> None:
        super().__init__()
        self._known_overrides_bad = known_overrides_bad
        self._account_manager = account_manager

    def validate(self, value: str) -> ValidationResult:
        super_result = super().validate(value)

        validators = [
            Function(self._validate_bad_account_in_input, self.BAD_ACCOUNT_IN_INPUT_FAILURE_DESCRIPTION),
        ]

        return ValidationResult.merge([super_result] + [validator.validate(value) for validator in validators])

    def _validate_bad_account_in_input(self, value: str) -> bool:
        if self._account_manager.is_account_known(value) and self._known_overrides_bad:
            return True

        return not self._account_manager.is_account_bad(value)
