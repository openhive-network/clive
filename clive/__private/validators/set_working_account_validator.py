from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.validation import Function, ValidationResult

from clive.__private.validators.bad_account_validator import BadAccountValidator

if TYPE_CHECKING:
    from clive.__private.core.profile import Profile


class SetWorkingAccountValidator(BadAccountValidator):
    ACCOUNT_ALREADY_WORKING_FAILURE: ClassVar[str] = "This account is already a working account."
    ACCOUNT_ALREADY_WATCHED_FAILURE: ClassVar[str] = "You cannot set account as working while its already watched."

    def __init__(self, profile: Profile) -> None:
        super().__init__(profile.accounts)
        self._profile = profile

    def validate(self, value: str) -> ValidationResult:
        super_result = super().validate(value)

        validators = [
            Function(self._validate_account_already_watched, self.ACCOUNT_ALREADY_WATCHED_FAILURE),
            Function(self._validate_account_already_working, self.ACCOUNT_ALREADY_WORKING_FAILURE),
        ]

        return ValidationResult.merge([super_result] + [validator.validate(value) for validator in validators])

    def _validate_account_already_watched(self, value: str) -> bool:
        return not self._profile.accounts.is_account_watched(value)

    def _validate_account_already_working(self, value: str) -> bool:
        return not self._profile.accounts.is_account_working(value)
