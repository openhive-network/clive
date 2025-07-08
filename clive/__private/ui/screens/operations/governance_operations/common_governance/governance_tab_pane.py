from __future__ import annotations

from abc import abstractmethod

from textual import on
from textual.widgets import TabPane

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.screens.operations.governance_operations.common_governance.governance_actions import (
    GovernanceActions,
)
from clive.__private.ui.screens.operations.governance_operations.common_governance.governance_table import (
    GovernanceTable,
    GovernanceTableRow,
)


class GovernanceTabPane(AbstractClassMessagePump, TabPane, CliveWidget):
    """TabPane with operation bindings and mechanism to handle with message to mount/unmount action."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: str, id_: str) -> None:
        super().__init__(title=title, id=id_)
        self._previous_operations = self.profile.transaction.operations

    def on_mount(self) -> None:
        self.watch(self.world, "profile_reactive", self.rebuild_actions_and_table)

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
            await actions.remove_row(identifier=event.action_identifier)
            self.remove_operation_from_cart(event.action_identifier, vote=event.vote)

    async def rebuild_actions_and_table(self) -> None:
        """
        Rebuild actions and table after operations in the cart changed.

        This is needed because user can go to cart and then back to governance screen.
        In cart user might remove some actions and we need to update their status.
        """
        current_operations = self.profile.transaction.operations

        if self._previous_operations == current_operations:
            return

        self._previous_operations = current_operations
        with self.app.batch_update():
            await self.query_exactly_one(GovernanceTable).reset_page()  # type: ignore[type-abstract]
            await self.query_exactly_one(GovernanceActions).rebuild()  # type: ignore[type-abstract]
