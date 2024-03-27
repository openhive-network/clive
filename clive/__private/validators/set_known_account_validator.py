from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.validation import Function, ValidationResult

from clive.__private.validators.account_name_validator import AccountNameValidator

if TYPE_CHECKING:
    from clive.__private.core.profile_data import ProfileData


class SetKnownAccountValidator(AccountNameValidator):
    ACCOUNT_ALREADY_KNOWN_FAILURE: Final[str] = "This account is already known."

    def __init__(self, profile_data: ProfileData) -> None:
        super().__init__()
        self._profile_data = profile_data

    def validate(self, value: str) -> ValidationResult:
        super_result = super().validate(value)

        validators = [
            Function(self._validate_account_already_known, self.ACCOUNT_ALREADY_KNOWN_FAILURE),
        ]

        return ValidationResult.merge([super_result] + [validator.validate(value) for validator in validators])

    def _validate_account_already_known(self, value: str) -> bool:
        return value not in [known_account.name for known_account in self._profile_data.known_accounts]
