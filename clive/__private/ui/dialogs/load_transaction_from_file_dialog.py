from __future__ import annotations

from clive.__private.core.commands.load_transaction import LoadTransactionError
from clive.__private.ui.dialogs.select_file_base_dialog import SelectFileBaseDialog
from clive.__private.visitors.operation.potential_known_account_visitor import PotentialKnownAccountCollector


class LoadTransactionFromFileDialog(SelectFileBaseDialog):
    def __init__(self) -> None:
        notice_text = (
            "Loading the transaction from the file will clear the current content of the cart."
            if self.profile.transaction
            else None
        )
        super().__init__("Choose a file to load the transaction", "Load file", notice=notice_text)

    def _add_known_accounts(self) -> None:
        visitor = PotentialKnownAccountCollector()
        self.profile.transaction.accept(visitor)
        unknown_accounts = visitor.get_unknown_accounts(self.profile.accounts.known)
        self.profile.accounts.add_known_account(*unknown_accounts)
        if unknown_accounts:
            accounts = ", ".join(unknown_accounts)
            self.notify(f"New accounts have been added to the list of known accounts: {accounts}.")

    async def _load_transaction_from_file(self) -> bool:
        file_path = self._file_path_input.value_or_none()

        if file_path is None:
            return False

        try:
            loaded_transaction = (await self.commands.load_transaction_from_file(path=file_path)).result_or_raise
        except LoadTransactionError as error:
            self.notify(f"Error occurred while loading transaction from file: {error}", severity="error")
            return False

        if not loaded_transaction.is_tapos_set:
            self.notify("TaPoS metadata was not set, updating automatically...")
            await self.commands.update_transaction_metadata(transaction=loaded_transaction)

        self.profile.transaction_file_path = file_path
        self.profile.transaction = loaded_transaction
        if self.profile.should_enable_known_accounts:
            self._add_known_accounts()
        self.app.trigger_profile_watchers()

        await self.app.action_go_to_transaction_summary()
        return True

    async def _perform_confirmation(self) -> bool:
        return await self._load_transaction_from_file()
