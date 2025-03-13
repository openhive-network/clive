from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive, var
from textual.widgets import Label

from clive.__private.core.constants.tui.bindings import REFRESH_TRANSACTION_METADATA_BINDING_KEY
from clive.__private.core.formatters import humanize
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.widgets.buttons import RefreshOneLineButton

if TYPE_CHECKING:
    from datetime import datetime

    from textual.app import ComposeResult

    from clive.__private.core.node import Node
    from clive.__private.models import Transaction


class TaposHolder(Vertical):
    """Container for the TaPoS metadata."""

    transaction: Transaction = var(None, init=False)  # type: ignore[assignment]

    def __init__(self, transaction: Transaction) -> None:
        super().__init__()
        self.set_reactive(self.__class__.transaction, transaction)  # type: ignore[arg-type]

    def watch_transaction(self) -> None:
        self._refresh_labels()

    def compose(self) -> ComposeResult:
        yield Label("TaPoS:")
        yield Label(self._generate_ref_block_num_text(), id="ref-block-num")
        yield Label(self._generate_ref_block_prefix_text(), id="ref-block-prefix")

    def _generate_ref_block_num_text(self) -> str:
        return f"Ref block num: {self.transaction.ref_block_num}"

    def _generate_ref_block_prefix_text(self) -> str:
        return f"Ref block prefix: {self.transaction.ref_block_prefix}"

    def _refresh_labels(self) -> None:
        self.query_exactly_one("#ref-block-num", Label).update(self._generate_ref_block_num_text())
        self.query_exactly_one("#ref-block-prefix", Label).update(self._generate_ref_block_prefix_text())


class TransactionExpirationLabel(Label):
    """Label for displaying transaction expiration."""

    expiration: datetime = reactive(None, init=False)  # type: ignore[assignment]

    def __init__(self, expiration: datetime) -> None:
        super().__init__()
        self.set_reactive(self.__class__.expiration, expiration)  # type: ignore[arg-type]

    def render(self) -> str:
        expiration = humanize.humanize_datetime(self.expiration)
        return f"Expiration: {expiration}"


class TransactionIdLabel(Label):
    """Label for displaying transaction id."""

    transaction_id: str = reactive(None, init=False)  # type: ignore[assignment]

    def __init__(self, transaction_id: str) -> None:
        super().__init__()
        self.set_reactive(self.__class__.transaction_id, transaction_id)  # type: ignore[arg-type]

    def render(self) -> str:
        return f"Transaction ID: {self.transaction_id}"


class RefreshMetadataButton(RefreshOneLineButton):
    def __init__(self) -> None:
        super().__init__(f"Refresh ({REFRESH_TRANSACTION_METADATA_BINDING_KEY.upper()})")
        self.watch(self.world, "node_reactive", self._handle_display)

    def _handle_display(self, node: Node) -> None:
        self.display = bool(node.cached.online_or_none)  # don't display refresh button when node is offline


class TransactionMetadataContainer(Horizontal, CliveWidget):
    """Container for the transaction metadata."""

    def compose(self) -> ComposeResult:
        if self.profile.transaction:
            yield TaposHolder(self.profile.transaction)
            yield TransactionExpirationLabel(self.profile.transaction.expiration)
            with Vertical(id="label-and-button-container"):
                yield TransactionIdLabel(self.profile.transaction.calculate_transaction_id())
                yield Container(RefreshMetadataButton())
        else:
            yield Label("No operations in cart, can't calculate transaction metadata.", id="no-metadata")

    @property
    def is_metadata_displayed(self) -> bool:
        return bool(self.query(TaposHolder))

    async def update_metadata_labels(self) -> None:
        """Recompose or just update values of already existing labels."""
        transaction = self.profile.transaction
        if not transaction or not self.is_metadata_displayed:
            await self.recompose()
            return

        tapos_holder = self.query_exactly_one(TaposHolder)
        tapos_holder.transaction = transaction
        tapos_holder.mutate_reactive(tapos_holder.__class__.transaction)  # type: ignore[arg-type]
        self.query_exactly_one(TransactionExpirationLabel).expiration = transaction.expiration
        self.query_exactly_one(TransactionIdLabel).transaction_id = transaction.calculate_transaction_id()
