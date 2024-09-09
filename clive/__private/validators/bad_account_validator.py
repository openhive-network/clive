from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.validation import Validator

if TYPE_CHECKING:
    from textual.validation import ValidationResult

    from clive.__private.core.accounts.account_manager import AccountManager


class BadAccountValidator(Validator):
    BAD_ACCOUNT_IN_INPUT_FAILURE_DESCRIPTION: Final[str] = "This account is considered as bad!"

    def __init__(self, account_manager: AccountManager, *, known_overrides_bad: bool = True) -> None:
        super().__init__()
        self._known_overrides_bad = known_overrides_bad
        self._account_manager = account_manager

    def validate(self, value: str) -> ValidationResult:
        account_manager = self._account_manager

        if not account_manager.is_account_bad(value) or self._should_pass_when_known(value, account_manager):
            return self.success()

        return self.failure(self.BAD_ACCOUNT_IN_INPUT_FAILURE_DESCRIPTION, value)

    def _should_pass_when_known(self, value: str, account_manager: AccountManager) -> bool:
        return account_manager.is_account_known(value) and self._known_overrides_bad
