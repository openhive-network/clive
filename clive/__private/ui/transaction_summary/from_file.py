from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Label

from clive.__private.ui.transaction_summary.common import KeyHint, TransactionSummaryCommon
from clive.__private.ui.widgets.select_file_to_save_transaction import SelectFileToSaveTransaction

if TYPE_CHECKING:
    from pathlib import Path

    from textual.app import ComposeResult

    from clive.__private.models import Transaction


class AlreadySignedHint(Label):
    """Hint about the already signed transaction."""

    DEFAULT_CSS = """
    AlreadySignedHint {
        margin: 1 0;
        color: $success;
    }
    """

    def __init__(self, transaction: Transaction) -> None:
        super().__init__("(This transaction is already signed)")
        self.display = transaction.is_signed()


class TransactionSummaryFromFile(TransactionSummaryCommon):
    def __init__(self, transaction: Transaction, file_path: Path) -> None:
        super().__init__()
        self.__transaction = transaction
        self.__file_path = file_path
        self.subtitle = f"Loaded from [blue]{self.__file_path}[/]"

    async def _initialize_transaction(self) -> Transaction:
        transaction = self.__transaction
        if not transaction.is_tapos_set():
            self.notify("TaPoS metadata was not set, updating automatically...")
            await self.commands.update_transaction_metadata(transaction=transaction)
        return transaction

    def action_save(self) -> None:
        self.app.push_screen(SelectFileToSaveTransaction())

    def _actions_container_content(self) -> ComposeResult:
        if self.__transaction.is_signed():
            yield AlreadySignedHint(self.__transaction)
        else:
            yield KeyHint("Sign with key:")
            yield self._select_key
