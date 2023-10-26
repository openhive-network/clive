from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Label

from clive.__private.core.formatters import humanize
from clive.__private.ui.transaction_summary.common import KeyHint, TransactionSummaryCommon
from clive.__private.ui.widgets.select_file_to_save_transaction import SelectFileToSaveTransaction

if TYPE_CHECKING:
    from pathlib import Path

    from rich.console import RenderableType
    from textual.app import ComposeResult

    from clive.models import Operation, Transaction


class AlreadySignedHint(Label):
    """Hint about the transaction."""

    DEFAULT_CSS = """
    AlreadySignedHint {
        margin: 1 0;
    }
    """

    def __init__(self, transaction: Transaction):
        message = (
            "(This transaction is already signed - expiration"
            f" {humanize.humanize_datetime(transaction.expiration)} UTC)"
        )
        super().__init__(message)
        self.display = transaction.is_signed()


class TransactionSummaryFromFile(TransactionSummaryCommon):
    def __init__(self, transaction: Transaction, file_path: Path) -> None:
        super().__init__()
        self.__transaction = transaction
        self.__file_path = file_path

    def action_save(self) -> None:
        self.app.push_screen(SelectFileToSaveTransaction(already_signed=self.__transaction.is_signed()))

    def _get_subtitle(self) -> RenderableType:
        return f"(Loaded from [blue]{self.__file_path}[/])"

    def _content_after_subtitle(self) -> ComposeResult:
        if self.__transaction.is_signed():
            yield AlreadySignedHint(self.__transaction)
        else:
            yield KeyHint("Sign with key:")
            yield self._select_key

    def _get_operations(self) -> list[Operation]:
        return self.__transaction.operations_models

    async def _get_transaction(self) -> Transaction:
        return self.__transaction
