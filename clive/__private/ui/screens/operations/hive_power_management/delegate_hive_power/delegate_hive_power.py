from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Horizontal
from textual.widgets import Static, TabPane

from clive.__private.core.constants.tui.class_names import CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME
from clive.__private.core.ensure_vests import ensure_vests
from clive.__private.models.schemas import DelegateVestingSharesOperation
from clive.__private.ui.data_providers.hive_power_data_provider import HivePowerDataProvider
from clive.__private.ui.dialogs.operation_summary.remove_delegation_dialog import RemoveDelegationDialog
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.not_updated_yet import NotUpdatedYet
from clive.__private.ui.screens.operations.bindings import OperationActionBindings
from clive.__private.ui.widgets.buttons import CliveButton, OneLineButton
from clive.__private.ui.widgets.clive_basic import (
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
from clive.__private.ui.widgets.inputs.hp_vests_amount_input import HPVestsAmountInput
from clive.__private.ui.widgets.inputs.receiver_input import ReceiverInput
from clive.__private.ui.widgets.place_taker import PlaceTaker
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section import Section
from clive.__private.ui.widgets.transaction_buttons import TransactionButtons

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.commands.data_retrieval.hive_power_data import HivePowerData
    from clive.__private.models.schemas import VestingDelegation


class DelegationsTableHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("Delegate", classes=CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME)
        yield Static("Shares [HP]", classes=CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME)
        yield Static("Shares [VESTS]", classes=CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME)
        yield PlaceTaker()


class Delegation(CliveCheckerboardTableRow):
    """
    Row of the `DelegationsTable`.

    Args:
        delegation: delegation data to display.
        aligned_hp_amount: aligned amount of hp to dots.
        aligned_vests_amount: aligned amount of vests to dots.
    """

    def __init__(self, delegation: VestingDelegation, aligned_hp_amount: str, aligned_vests_amount: str) -> None:
        """
        Initialize the delegation row.

        Args:
        ----
        delegation: delegation data to display.
        aligned_hp_amount: aligned amount of hp to dots.
        aligned_vests_amount: aligned amount of vests to dots.
        """
        self._aligned_hp_amount = aligned_hp_amount

        super().__init__(
            CliveCheckerBoardTableCell(delegation.delegatee),
            CliveCheckerBoardTableCell(aligned_hp_amount),
            CliveCheckerBoardTableCell(aligned_vests_amount),
            CliveCheckerBoardTableCell(OneLineButton("Remove", id_="remove-delegation-button", variant="error")),
        )
        self._delegation = delegation

    @on(CliveButton.Pressed, "#remove-delegation-button")
    def push_operation_summary_screen(self) -> None:
        self.app.push_screen(RemoveDelegationDialog(self._delegation, self._aligned_hp_amount))


class DelegationsTable(CliveCheckerboardTable):
    """Table with delegations."""

    ATTRIBUTE_TO_WATCH = "_content"
    NO_CONTENT_TEXT = "You have no delegations"

    def __init__(self) -> None:
        super().__init__(header=DelegationsTableHeader(), title="Current delegations", init_dynamic=False)
        self._previous_delegations: list[VestingDelegation] | NotUpdatedYet = NotUpdatedYet()

    def create_dynamic_rows(self, content: HivePowerData) -> list[Delegation]:
        aligned_hp, aligned_vests = content.get_delegations_aligned_amounts()

        return [
            Delegation(delegation, hp_value, vests_value)
            for delegation, hp_value, vests_value in zip(content.delegations, aligned_hp, aligned_vests, strict=True)
        ]

    def check_if_should_be_updated(self, content: HivePowerData) -> bool:
        return self._previous_delegations != content.delegations

    def is_anything_to_display(self, content: HivePowerData) -> bool:
        return len(content.delegations) != 0

    @property
    def object_to_watch(self) -> HivePowerDataProvider:
        return self.screen.query_exactly_one(HivePowerDataProvider)

    def update_previous_state(self, content: HivePowerData) -> None:
        self._previous_delegations = content.delegations


class DelegateHivePower(TabPane, OperationActionBindings):
    """TabPane with all content about delegate hp."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self) -> None:
        super().__init__(title="Delegate")
        self._delegate_input = ReceiverInput("Delegate")
        self._shares_input = HPVestsAmountInput()

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            with Section("Delegate your shares"):
                yield self._delegate_input
                yield self._shares_input
                yield TransactionButtons()
            yield DelegationsTable()

    def _create_operation(self) -> DelegateVestingSharesOperation | None:
        if not CliveValidatedInput.validate_many(self._delegate_input, self._shares_input):
            return None

        asset = self._shares_input.value_or_error

        # If the user has passed an amount in `HP` - convert it to `VESTS`. The operation is performed using VESTS.
        asset = ensure_vests(asset, self.provider.content.gdpo)
        return DelegateVestingSharesOperation(
            delegator=self.profile.accounts.working.name,
            delegatee=self._delegate_input.value_or_error,
            vesting_shares=asset,
        )

    @property
    def provider(self) -> HivePowerDataProvider:
        return self.screen.query_exactly_one(HivePowerDataProvider)
