from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal

from clive.__private.ui.widgets.buttons import AddToCartButton, FinalizeTransactionButton

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.binding import Binding


class TransactionButtons(Horizontal):
    DEFAULT_CSS = """
    TransactionButtons {
        align: center middle;
        height: auto;

        FinalizeTransactionButton {
            margin-left: 1;
        }
    }
    """

    def __init__(self, bindings_list: list[Binding]) -> None:
        super().__init__()
        self._bindings_list = bindings_list

    def compose(self) -> ComposeResult:
        yield AddToCartButton(self._bindings_list)
        yield FinalizeTransactionButton(self._bindings_list)
