from __future__ import annotations

from textual import on
from textual.binding import Binding
from textual.widgets import TabPane

from clive.__private.core.constants.tui.bindings import (
    ADD_OPERATION_TO_CART_BINDING_KEY,
    FINALIZE_TRANSACTION_BINDING_KEY,
)
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.screens.operations.bindings import OperationActionBindings
from clive.__private.ui.screens.operations.governance_operations.common_governance.governance_actions import (
    GovernanceActions,
)
from clive.__private.ui.screens.operations.governance_operations.common_governance.governance_table import (
    GovernanceTableRow,
)


class GovernanceTabPane(TabPane, OperationActionBindings):
    """TabPane with operation bindings and mechanism to handle with message to mount/unmount action."""

    BINDINGS = [
        Binding(ADD_OPERATION_TO_CART_BINDING_KEY, "add_to_cart", "Add to cart"),
        Binding(FINALIZE_TRANSACTION_BINDING_KEY, "finalize_transaction", "Finalize transaction"),
    ]

    DEFAULT_CSS = get_css_from_relative_path(__file__)
    POP_SCREEN_AFTER_ADDING_TO_CART = True

    @on(GovernanceTableRow.ChangeActionStatus)
    async def change_action_status(self, event: GovernanceTableRow.ChangeActionStatus) -> None:
        actions = self.query_exactly_one(GovernanceActions)  # type: ignore[type-abstract]

        if event.add:
            await actions.add_row(identifier=event.action_identifier, vote=event.vote)
        else:
            await actions.remove_row(identifier=event.action_identifier, vote=event.vote)
