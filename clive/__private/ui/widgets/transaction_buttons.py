from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal

from clive.__private.ui.widgets.buttons import AddToCartButton, FinalizeTransactionButton

if TYPE_CHECKING:
    from textual.app import ComposeResult


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

    def compose(self) -> ComposeResult:
        yield AddToCartButton()
        yield FinalizeTransactionButton()
