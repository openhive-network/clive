from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.validation import Validator

from wax.exceptions.chain_errors import PrivateKeyDetectedInMemoError
from wax.models.authority import WaxAuthorities

if TYPE_CHECKING:
    from textual.validation import ValidationResult

    from clive.__private.core.accounts.account_manager import AccountManager
    from wax import IHiveChainInterface


class PrivateKeyInMemoValidator(Validator):
    PRIVATE_KEY_IN_MEMO_FAILURE_DESCRIPTION: Final[str] = "Private key detected"

    def __init__(self, wax_interface: IHiveChainInterface, account_manager: AccountManager) -> None:
        super().__init__()
        self._wax_interface = wax_interface
        self._account_manager = account_manager

    def validate(self, memo_value: str) -> ValidationResult:
        for account in self._account_manager.tracked:
            operation = account.data.authority.operation
            authorities = WaxAuthorities(
                owner=operation.categories.hive.authorities.owner.value,
                active=operation.categories.hive.authorities.active.value,
                posting=operation.categories.hive.authorities.posting.value,
            )
            try:
                self._wax_interface.scan_text_for_matching_private_keys(
                    content=memo_value,
                    account=account.name,
                    account_authorities=authorities,
                    memo_key=operation.categories.hive.authorities.memo.value,
                )
            except PrivateKeyDetectedInMemoError:
                return self.failure(self.PRIVATE_KEY_IN_MEMO_FAILURE_DESCRIPTION, memo_value)
        return self.success()
