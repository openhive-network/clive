from __future__ import annotations

from textual import on
from textual.containers import ScrollableContainer
from textual.widgets import TabPane

from clive.__private.ui.operations.bindings import OperationActionBindings
from clive.__private.ui.operations.governance_operations.common_governance.governance_actions import (
    GovernanceActions,
)
from clive.__private.ui.operations.governance_operations.common_governance.governance_table import (
    GovernanceTableRow,
)


class ScrollablePart(ScrollableContainer, can_focus=False):
    pass


class GovernanceTabPane(TabPane, OperationActionBindings):
    """TabPane with operation bindings and mechanism to handle with message to mount/unmount action."""

    @on(GovernanceTableRow.ChangeActionStatus)
    async def change_action_status(self, event: GovernanceTableRow.ChangeActionStatus) -> None:
        actions = self.query_one(GovernanceActions)  # type: ignore[type-abstract]

        if event.add:
            await actions.add_row(identifier=event.action_identifier, vote=event.vote)
        else:
            await actions.remove_row(identifier=event.action_identifier, vote=event.vote)
