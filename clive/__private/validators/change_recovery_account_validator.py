from __future__ import annotations

from typing import Final

from textual.validation import Function, ValidationResult

from clive.__private.core.constants.alarms import WARNING_RECOVERY_ACCOUNTS
from clive.__private.validators.account_name_validator import AccountNameValidator


class ChangeRecoveryAccountValidator(AccountNameValidator):
    WARNING_RECOVERY_ACCOUNT_FAILURE_DESCRIPTION: Final[str] = "This account is considered unsafe as recovery account!"

    def validate(self, value: str) -> ValidationResult:
        super_result = super().validate(value)

        validators = [
            Function(self._validate_warning_account, self.WARNING_RECOVERY_ACCOUNT_FAILURE_DESCRIPTION),
        ]

        return ValidationResult.merge([super_result] + [validator.validate(value) for validator in validators])

    def _validate_warning_account(self, value: str) -> bool:
        return value not in WARNING_RECOVERY_ACCOUNTS
