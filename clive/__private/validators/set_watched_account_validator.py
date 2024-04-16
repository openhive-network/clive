from __future__ import annotations

from typing import ClassVar, Final

from textual.validation import Function, ValidationResult

from clive.__private.validators.set_working_account_validator import SetWorkingAccountValidator


class SetWatchedAccountValidator(SetWorkingAccountValidator):
    ACCOUNT_ALREADY_WATCHED_FAILURE: ClassVar[str] = "This account is already being watched."
    ACCOUNT_ALREADY_WORKING_FAILURE: ClassVar[str] = "You cannot watch your working account."

    MAX_NUMBER_OF_WATCHED_ACCOUNTS: Final[int] = 5
    MAX_NUMBER_OF_WATCHED_ACCOUNTS_FAILURE: Final[str] = (
        f"You can only watch {MAX_NUMBER_OF_WATCHED_ACCOUNTS} accounts."
    )

    def validate(self, value: str) -> ValidationResult:
        super_result = super().validate(value)

        validators = [
            Function(self._validate_max_watched_accounts_reached, self.MAX_NUMBER_OF_WATCHED_ACCOUNTS_FAILURE),
        ]

        return ValidationResult.merge([super_result] + [validator.validate(value) for validator in validators])

    def _validate_max_watched_accounts_reached(self, _: str) -> bool:
        return len(self._profile_data.watched_accounts) < self.MAX_NUMBER_OF_WATCHED_ACCOUNTS
