from __future__ import annotations

from textual.binding import Binding

from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.screens.transaction_summary import TransactionSummary


class TransactionSummaryBinding(CliveWidget):
    BINDINGS = [
        Binding("f2", "transaction_summary", "Transaction summary"),
    ]

    async def action_transaction_summary(self) -> None:
        transaction = self.profile.transaction
        if not transaction.is_signed and transaction:
            await self.commands.update_transaction_metadata(transaction=transaction)
        await self.app.push_screen(TransactionSummary())
