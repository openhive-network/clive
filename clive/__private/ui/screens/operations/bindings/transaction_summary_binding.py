from __future__ import annotations

from clive.__private.ui.bindings import CLIVE_PREDEFINED_BINDINGS
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.screens.transaction_summary import TransactionSummary


class TransactionSummaryBinding(CliveWidget):
    BINDINGS = [CLIVE_PREDEFINED_BINDINGS.app.transaction_summary.create()]

    async def action_transaction_summary(self) -> None:
        if not self.profile.transaction.is_signed:
            await self.commands.update_transaction_metadata(transaction=self.profile.transaction)
        await self.app.push_screen(TransactionSummary())
