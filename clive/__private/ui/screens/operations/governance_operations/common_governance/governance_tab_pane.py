from __future__ import annotations

from textual import on
from textual.widgets import TabPane

from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.screens.operation_base_screen import OperationBaseScreen
from clive.__private.ui.screens.operations.bindings import OperationActionBindings
from clive.__private.ui.screens.operations.governance_operations.common_governance.governance_actions import (
    GovernanceActions,
)
from clive.__private.ui.screens.operations.governance_operations.common_governance.governance_table import (
    GovernanceTable,
    GovernanceTableRow,
)


class GovernanceTabPane(TabPane, OperationActionBindings):
    """TabPane with operation bindings and mechanism to handle with message to mount/unmount action."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    @on(OperationActionBindings.OperationAddedToCart)
    @on(OperationBaseScreen.Resumed)
    async def restore_actions_and_table(self) -> None:
        await self.query_exactly_one(GovernanceActions).restore()  # type: ignore[type-abstract]
        await self.query_exactly_one(GovernanceTable).reset_page()  # type: ignore[type-abstract]

    @on(GovernanceTableRow.ChangeActionStatus)
    async def change_action_status(self, event: GovernanceTableRow.ChangeActionStatus) -> None:
        actions = self.query_exactly_one(GovernanceActions)  # type: ignore[type-abstract]

        match event.status:
            case "pending_vote":
                await actions.remove_row(
                    identifier=event.action_identifier, operation_entity=event.operation_entity, vote=True, pending=True
                )
            case "pending_unvote":
                await actions.remove_row(
                    identifier=event.action_identifier,
                    operation_entity=event.operation_entity,
                    vote=False,
                    pending=True,
                )
            case _:
                if event.add:
                    await actions.add_row(identifier=event.action_identifier, vote=event.status == "vote")
                else:
                    await actions.remove_row(identifier=event.action_identifier, vote=event.status == "vote")
