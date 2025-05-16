from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Label

from clive.__private.core.constants.tui.bindings import REFRESH_TRANSACTION_METADATA_BINDING_KEY
from clive.__private.core.formatters import humanize
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.widgets.buttons import RefreshOneLineButton

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.node import Node
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


class RefreshMetadataButton(RefreshOneLineButton):
    def __init__(self) -> None:
        super().__init__(f"Refresh metadata ({REFRESH_TRANSACTION_METADATA_BINDING_KEY.upper()})")
        self.watch(self.world, "node_reactive", self._handle_display)

    def _handle_display(self, node: Node) -> None:
        self.display = bool(node.cached.online_or_none)  # don't display refresh button when node is offline


class TransactionMetadataContainer(Horizontal, CliveWidget):
    """Container for the transaction metadata."""

    def compose(self) -> ComposeResult:
        if self.profile.transaction:
            expiration = humanize.humanize_datetime(self.profile.transaction.expiration)
            yield TaposHolder(self.profile.transaction)
            yield TransactionExpirationLabel(f"Expiration: {expiration}")
            with Vertical(id="label-and-button-container"):
                yield TransactionIdLabel(f"Transaction ID: {self.profile.transaction.calculate_transaction_id()}")
                yield Container(RefreshMetadataButton())
        else:
            yield Label("No operations in cart, can't calculate transaction metadata.", id="no-metadata")
