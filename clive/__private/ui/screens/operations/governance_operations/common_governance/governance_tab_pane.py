from __future__ import annotations

from textual import on
from textual.widgets import TabPane

from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.screens.operation_base_screen import OperationBaseScreen
from clive.__private.ui.screens.operations.governance_operations.common_governance.governance_actions import (
    GovernanceActions,
)
from clive.__private.ui.screens.operations.governance_operations.common_governance.governance_table import (
    GovernanceTable,
    GovernanceTableRow,
)


class GovernanceTabPane(TabPane):
    """TabPane with operation bindings and mechanism to handle with message to mount/unmount action."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    @on(GovernanceTableRow.ChangeActionStatus)
    async def change_action_status(self, event: GovernanceTableRow.ChangeActionStatus) -> None:
        actions = self.query_exactly_one(GovernanceActions)  # type: ignore[type-abstract]

        if event.add:
            await actions.add_row(identifier=event.action_identifier, vote=event.vote)
            actions.add_operation_to_cart(event.action_identifier, vote=event.vote)
        else:
            await actions.remove_row(identifier=event.action_identifier, vote=event.vote)
            actions.remove_operation_from_cart(event.action_identifier, vote=event.vote)

    @on(OperationBaseScreen.Resumed)
    async def restore_actions_and_table(self) -> None:
        """
        Restore actions and table after screen is resumed.

        This is needed because user can go to cart and then back to governance screen.
        In cart user might remove some actions and we need to update their status.
        """
        with self.app.batch_update():
            await self.query_exactly_one(GovernanceTable).reset_page()  # type: ignore[type-abstract]
            await self.query_exactly_one(GovernanceActions).rebuild()  # type: ignore[type-abstract]
