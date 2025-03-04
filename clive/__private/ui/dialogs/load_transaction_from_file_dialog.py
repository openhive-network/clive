from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.load_transaction import LoadTransactionError
from clive.__private.core.constants.tui.messages import (
    BAD_ACCOUNT_IN_LOADED_TRANSACTION_MESSAGE,
    ERROR_BAD_ACCOUNT_IN_LOADED_TRANSACTION_MESSAGE,
)
from clive.__private.ui.dialogs.select_file_base_dialog import SelectFileBaseDialog

if TYPE_CHECKING:
    from clive.__private.models import Transaction


class LoadTransactionFromFileDialog(SelectFileBaseDialog[bool]):
    def __init__(self) -> None:
        notice_text = (
            "Loading the transaction from the file will clear the current content of the cart."
            if self.profile.transaction
            else None
        )
        super().__init__("Choose a file to load the transaction", "Load file", notice=notice_text)

    def _add_known_accounts(self) -> None:
        unknown_accounts = self.profile.transaction.get_unknown_accounts(self.profile.accounts.known)
        self.profile.accounts.add_known_account(*unknown_accounts)
        if unknown_accounts:
            accounts = ", ".join(unknown_accounts)
            self.notify(f"New accounts have been added to the list of known accounts: {accounts}.")

    def _check_for_unknown_bad_accounts(self, loaded_transaction: Transaction) -> bool:
        """
        Check if the loaded transaction contains any bad accounts.

        Returns:
            True: If the transaction has bad accounts that are unknown, and notifies the user with an error message.
            False: If the transaction does not have any bad accounts or if the bad accounts are known,
                   and notifies the user with a warning message.
        """
        bad_accounts = loaded_transaction.get_bad_accounts(self.profile.accounts.get_bad_accounts())
        if not bad_accounts:
            return False

        unknown_accounts = loaded_transaction.get_unknown_accounts(self.profile.accounts.known)
        has_unknown_bad_account = any(bad_account in unknown_accounts for bad_account in bad_accounts)

        if has_unknown_bad_account:
            self.notify(ERROR_BAD_ACCOUNT_IN_LOADED_TRANSACTION_MESSAGE, severity="error")
            return True

        self.notify(BAD_ACCOUNT_IN_LOADED_TRANSACTION_MESSAGE, severity="warning")
        return False

    async def _load_transaction_from_file(self) -> bool:
        file_path = self._file_path_input.value_or_none()

        if file_path is None:
            return False

        try:
            loaded_transaction = (await self.commands.load_transaction_from_file(path=file_path)).result_or_raise
        except LoadTransactionError as error:
            self.notify(f"Error occurred while loading transaction from file: {error}", severity="error")
            return False

        if self._check_for_unknown_bad_accounts(loaded_transaction):
            return False

        if not loaded_transaction.is_tapos_set:
            self.notify("TaPoS metadata was not set, updating automatically...")
            await self.commands.update_transaction_metadata(transaction=loaded_transaction)

        self.profile.transaction_file_path = file_path
        self.profile.transaction = loaded_transaction
        if self.profile.should_enable_known_accounts:
            self._add_known_accounts()
        self.app.trigger_profile_watchers()

        self.call_later(self.app.action_go_to_transaction_summary)
        return True

    async def _perform_confirmation(self) -> bool:
        return await self._load_transaction_from_file()
