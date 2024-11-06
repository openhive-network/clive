from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Label

from clive.__private.core.formatters import humanize

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.models import Transaction


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


class TransactionMetadataContainer(Horizontal):
    """Container for the transaction metadata."""

    transaction: Transaction = reactive(None, recompose=True, always_update=True)  # type: ignore[assignment]

    def __init__(self, transaction: Transaction) -> None:
        super().__init__()
        self.transaction = transaction

    def compose(self) -> ComposeResult:
        if self.transaction:
            expiration = humanize.humanize_datetime(self.transaction.expiration)
            yield TaposHolder(self.transaction)
            yield TransactionExpirationLabel(f"Expiration: {expiration}")
            yield TransactionIdLabel(f"Transaction ID: {self.transaction.calculate_transaction_id()}")
        else:
            yield Label("No operations in cart, can't calculate transaction metadata.", id="no-metadata")
