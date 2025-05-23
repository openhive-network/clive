from __future__ import annotations

from textual.binding import Binding

from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.screens.transaction_summary import TransactionSummary


class TransactionSummaryBinding(CliveWidget):
    BINDINGS = [
        Binding("f2", "transaction_summary", "Transaction summary"),
    ]

    async def action_transaction_summary(self) -> None:
        if not self.profile.transaction.is_signed:
            await self.commands.update_transaction_metadata(transaction=self.profile.transaction)
        await self.app.push_screen(TransactionSummary())
