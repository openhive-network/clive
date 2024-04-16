from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.validation import Function, ValidationResult

from clive.__private.validators.account_name_validator import AccountNameValidator

if TYPE_CHECKING:
    from clive.__private.core.profile_data import ProfileData


class SetWorkingAccountValidator(AccountNameValidator):
    ACCOUNT_ALREADY_WORKING_FAILURE: ClassVar[str] = "This account is already a working account."
    ACCOUNT_ALREADY_WATCHED_FAILURE: ClassVar[str] = "You cannot set account as working while its already watched."

    def __init__(self, profile_data: ProfileData) -> None:
        super().__init__()
        self._profile_data = profile_data

    def validate(self, value: str) -> ValidationResult:
        super_result = super().validate(value)

        validators = [
            Function(self._validate_account_already_watched, self.ACCOUNT_ALREADY_WATCHED_FAILURE),
            Function(self._validate_account_already_working, self.ACCOUNT_ALREADY_WORKING_FAILURE),
        ]

        return ValidationResult.merge([super_result] + [validator.validate(value) for validator in validators])

    def _validate_account_already_watched(self, value: str) -> bool:
        return value not in [watched_account.name for watched_account in self._profile_data.watched_accounts]

    def _validate_account_already_working(self, value: str) -> bool:
        if not self._profile_data.is_working_account_set():
            return True

        return value != self._profile_data.working_account.name
