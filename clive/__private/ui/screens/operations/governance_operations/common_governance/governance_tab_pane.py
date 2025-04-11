from __future__ import annotations

from abc import abstractmethod

from textual import on
from textual.widgets import TabPane

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.screens.operations.governance_operations.common_governance.governance_actions import (
    GovernanceActions,
)
from clive.__private.ui.screens.operations.governance_operations.common_governance.governance_table import (
    GovernanceTableRow,
)


class GovernanceTabPane(AbstractClassMessagePump, TabPane):
    """TabPane with operation bindings and mechanism to handle with message to mount/unmount action."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    @abstractmethod
    def add_operation_to_cart(self, identifier: str, *, vote: bool) -> None:
        """Add operation to the cart."""

    @abstractmethod
    def remove_operation_from_cart(self, identifier: str, *, vote: bool) -> None:
        """Remove operation from the cart."""

    @on(GovernanceTableRow.ChangeActionStatus)
    async def change_action_status(self, event: GovernanceTableRow.ChangeActionStatus) -> None:
        actions = self.query_exactly_one(GovernanceActions)  # type: ignore[type-abstract]

        if event.add:
            await actions.add_row(identifier=event.action_identifier, vote=event.vote)
            self.add_operation_to_cart(event.action_identifier, vote=event.vote)
        else:
            await actions.remove_row(identifier=event.action_identifier, vote=event.vote)
            self.remove_operation_from_cart(event.action_identifier, vote=event.vote)
