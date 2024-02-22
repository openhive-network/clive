from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.widgets import Static, TabPane

from clive.__private.core.hive_vests_conversions import hive_to_vests, vests_to_hive
from clive.__private.ui.data_providers.hive_power_data_provider import HivePowerDataProvider
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.operations.bindings import OperationActionBindings
from clive.__private.ui.operations.hive_power_management.common_hive_power.hp_vests_factor import HpVestsFactor
from clive.__private.ui.operations.operation_summary.remove_delegation import RemoveDelegation
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_checkerboard_table import (
    EVEN_CLASS_NAME,
    ODD_CLASS_NAME,
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.currency_selector.currency_selector_hp_vests import CurrencySelectorHpVests
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
from clive.__private.ui.widgets.inputs.hp_vests_amount_input import HPVestsAmountInput
from clive.__private.ui.widgets.section_title import SectionTitle
from clive.models import Asset
from schemas.operations import DelegateVestingSharesOperation

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.__private.core.commands.data_retrieval.hive_power_data import HivePowerData
    from clive.models.aliased import DynamicGlobalProperties, VestingDelegation


class PlaceTaker(Static):
    pass


class ScrollablePart(ScrollableContainer, can_focus=False):
    pass


class DelegationsTableHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("Delegate", classes=ODD_CLASS_NAME)
        yield Static("Shares [HP]", classes=EVEN_CLASS_NAME)
        yield Static("Shares [VESTS]", classes=ODD_CLASS_NAME)
        yield PlaceTaker()


class Delegation(CliveCheckerboardTableRow):
    """Row of the `DelegationsTable`."""

    def __init__(self, delegation: VestingDelegation[Asset.Vests], dgpo: DynamicGlobalProperties) -> None:
        """
        Initialize the delegation row.

        Args:
        ----
        delegation: delegation data to display.
        dgpo: dynamic global properties.
        """
        self._amount_in_hp = vests_to_hive(delegation.vesting_shares, dgpo)
        super().__init__(
            CliveCheckerBoardTableCell(delegation.delegatee),
            CliveCheckerBoardTableCell(f"{Asset.pretty_amount(self._amount_in_hp)}"),
            CliveCheckerBoardTableCell(f"{Asset.pretty_amount(delegation.vesting_shares)}"),
            CliveCheckerBoardTableCell(CliveButton("Remove", id_="remove-delegation-button", variant="error")),
        )
        self._delegation = delegation

    @on(CliveButton.Pressed, "#remove-delegation-button")
    def push_operation_summary_screen(self) -> None:
        self.app.push_screen(RemoveDelegation(self._delegation, self._amount_in_hp))


class DelegationsTable(CliveCheckerboardTable):
    """Table with delegations."""

    def __init__(self) -> None:
        super().__init__(
            Static("Current delegations", id="delegations-table-title"), DelegationsTableHeader(), dynamic=True
        )
        self._previous_delegations: list[VestingDelegation[Asset.Vests]] | None = None

    def create_dynamic_rows(self, content: HivePowerData) -> list[Delegation]:
        self._previous_delegations = content.delegations

        return [Delegation(delegation, content.gdpo) for delegation in content.delegations]

    def get_no_content_available_widget(self) -> Static:
        return Static("You have no delegations", id="no-delegations-info")

    @property
    def check_if_should_be_updated(self) -> bool:
        return self._previous_delegations != self.provider.content.delegations

    @property
    def is_anything_to_display(self) -> bool:
        return len(self.provider.content.delegations) != 0

    @property
    def provider(self) -> HivePowerDataProvider:
        return self.screen.query_one(HivePowerDataProvider)


class DelegateHivePower(TabPane, OperationActionBindings):
    """TabPane with all content about delegate hp."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: TextType):
        """
        Initialize a TabPane.

        Args:
        ----
        title: Title of the TabPane (will be displayed in a tab label).
        """
        super().__init__(title=title)
        self._delegate_input = AccountNameInput("Delegate")
        self._shares_input = HPVestsAmountInput()

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield HpVestsFactor(self.provider)
            yield SectionTitle("Delegate your shares")
            with Vertical(id="inputs-container"):
                yield self._delegate_input
                yield self._shares_input
            yield DelegationsTable()

    def _create_operation(self) -> DelegateVestingSharesOperation | None:
        if not CliveValidatedInput.validate_many(self._delegate_input, self._shares_input):
            return None

        asset = self._shares_input.value_or_error

        if isinstance(asset, Asset.Hive):
            # If the user has passed an amount in `HP` - convert it to `VESTS`. The operation is performed using VESTS.
            asset = hive_to_vests(asset, self.provider.content.gdpo)
        return DelegateVestingSharesOperation(
            delegator=self.working_account, delegatee=self._delegate_input.value_or_error, vesting_shares=asset
        )

    @on(CurrencySelectorHpVests.Changed)
    def shares_type_changed(self) -> None:
        """Clear input when shares type was changed and hide factor display when vests selected."""
        self._shares_input.input.clear()

        hp_vests_factor = self.query_one(HpVestsFactor)
        if self._shares_input.selected_asset_type is Asset.Vests:
            hp_vests_factor.display = False
            return
        hp_vests_factor.display = True

    @property
    def provider(self) -> HivePowerDataProvider:
        return self.screen.query_one(HivePowerDataProvider)

    @property
    def working_account(self) -> str:
        return self.app.world.profile_data.working_account.name
