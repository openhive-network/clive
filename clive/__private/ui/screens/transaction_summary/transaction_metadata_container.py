from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Label

from clive.__private.core.formatters import humanize
from clive.__private.models import Transaction
from clive.__private.ui.widgets.buttons import RefreshOneLineButton

if TYPE_CHECKING:
    from textual.app import ComposeResult


class TaposHolder(Vertical):
    """Container for the TaPoS metadata."""

    def __init__(self, transaction: Transaction) -> None:
        super().__init__()
        self._transaction = transaction

    def compose(self) -> ComposeResult:
        yield Label("TaPoS:")
        yield Label(f"Ref block num: {self._transaction.ref_block_num}", id="ref-block-num")
        yield Label(f"Ref block prefix: {self._transaction.ref_block_prefix}", id="ref-block-prefix")


class TransactionExpirationLabel(Label):
    """Label for displaying transaction expiration."""


class TransactionIdLabel(Label):
    """Label for displaying transaction id."""


class RefreshMetadataButton(RefreshOneLineButton):
    def __init__(self) -> None:
        super().__init__()
        self._handle_display()
        self.watch(self.world, "node", self._handle_display)

    def _handle_display(self) -> None:
        self.display = bool(self.node.cached.online_or_none)  # don't display refresh button when node is offline


class TransactionMetadataContainer(Horizontal):
    """Container for the transaction metadata."""

    transaction: Transaction = reactive(Transaction(), recompose=True)  # type: ignore[assignment]

    def __init__(self, transaction: Transaction) -> None:
        super().__init__()
        self.transaction = transaction

    def compose(self) -> ComposeResult:
        if self.transaction:
            expiration = humanize.humanize_datetime(self.transaction.expiration)
            yield TaposHolder(self.transaction)
            yield TransactionExpirationLabel(f"Expiration: {expiration}")
            yield Vertical(
                TransactionIdLabel(f"Transaction ID: {self.transaction.calculate_transaction_id()}"),
                Container(RefreshMetadataButton()),
                id="label-and-button-container",
            )
        else:
            yield Label("No operations in cart, can't calculate transaction metadata.", id="no-metadata")
