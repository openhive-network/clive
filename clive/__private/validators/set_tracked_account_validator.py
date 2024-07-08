from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final

from textual.validation import Function, ValidationResult

from clive.__private.config import settings
from clive.__private.validators.account_name_validator import AccountNameValidator

if TYPE_CHECKING:
    from clive.__private.core.profile_data import ProfileData


class SetTrackedAccountValidator(AccountNameValidator):
    MAX_NUMBER_OF_TRACKED_ACCOUNTS: Final[int] = settings.get("MAX_NUMBER_OF_TRACKED_ACCOUNTS", 6)
    MAX_NUMBER_OF_TRACKED_ACCOUNTS_FAILURE: Final[str] = (
        f"You can only track {MAX_NUMBER_OF_TRACKED_ACCOUNTS} accounts."
    )
    ACCOUNT_ALREADY_TRACKED_FAILURE: ClassVar[str] = "You cannot track account while its already tracked."

    def __init__(self, profile_data: ProfileData) -> None:
        super().__init__()
        self._profile_data = profile_data

    def validate(self, value: str) -> ValidationResult:
        super_result = super().validate(value)

        validators = [
            Function(self._validate_account_already_tracked, self.ACCOUNT_ALREADY_TRACKED_FAILURE),
            Function(self._validate_max_tracked_accounts_reached, self.MAX_NUMBER_OF_TRACKED_ACCOUNTS_FAILURE),
        ]

        return ValidationResult.merge([super_result] + [validator.validate(value) for validator in validators])

    def _validate_account_already_tracked(self, value: str) -> bool:
        return self._profile_data.is_account_tracked(value)

    def _validate_max_tracked_accounts_reached(self, _: str) -> bool:
        return len(self._profile_data.get_tracked_accounts()) < self.MAX_NUMBER_OF_TRACKED_ACCOUNTS
