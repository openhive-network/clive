from __future__ import annotations

from textual.binding import Binding

from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.screens.transaction_summary.transaction_summary import TransactionSummary


class TransactionSummaryBinding(CliveWidget):
    BINDINGS = [
        Binding("f2", "transaction_summary", "Transaction summary"),
    ]

    def action_transaction_summary(self) -> None:
        self.app.push_screen(TransactionSummary())
