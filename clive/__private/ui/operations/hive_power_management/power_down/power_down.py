from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from textual import on
from textual.containers import Horizontal, ScrollableContainer
from textual.widgets import Pretty, Static, TabPane

from clive.__private.core.constants import HIVE_PERCENT_PRECISION
from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.core.hive_vests_conversions import hive_to_vests
from clive.__private.ui.data_providers.hive_power_data_provider import HivePowerDataProvider
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.operations.bindings.operation_action_bindings import OperationActionBindings
from clive.__private.ui.operations.hive_power_management.common_hive_power.hp_vests_factor import HpVestsFactor
from clive.__private.ui.operations.operation_summary.cancel_power_down import CancelPowerDown
from clive.__private.ui.widgets.can_focus_with_scrollbars_only import CanFocusWithScrollbarsOnly
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_checkerboard_table import (
    EVEN_CLASS_NAME,
    ODD_CLASS_NAME,
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.currency_selector.currency_selector_hp_vests import CurrencySelectorHpVests
from clive.__private.ui.widgets.generous_button import GenerousButton
from clive.__private.ui.widgets.inputs.hp_vests_amount_input import HPVestsAmountInput
from clive.__private.ui.widgets.notice import Notice
from clive.__private.ui.widgets.section_title import SectionTitle
from clive.models import Asset
from schemas.operations import WithdrawVestingOperation

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.__private.core.commands.data_retrieval.hive_power_data import HivePowerData


class PlaceTaker(Static):
    pass


class ScrollablePart(ScrollableContainer, CanFocusWithScrollbarsOnly):
    pass


class WithdrawRoutesDisplay(CliveWidget):
    """Widget used just to inform user to which account has withdrawal route and how much % it is."""

    def __init__(self) -> None:
        super().__init__()
        self._pretty = Pretty({})
        self._pretty.display = False

    def compose(self) -> ComposeResult:
        yield Static("Loading...", id="withdraw-routes-header")
        yield self._pretty

    def on_mount(self) -> None:
        self.watch(self.provider, "_content", self._update_withdraw_routes, init=False)

    def _update_withdraw_routes(self, content: HivePowerData) -> None:
        """Update withdraw routes pretty widget."""
        if not content.withdraw_routes:
            self.query_one("#withdraw-routes-header", Static).update("You have no withdraw routes")
            self._pretty.display = False
            return

        withdraw_routes = {
            withdraw_route.to_account: f"{withdraw_route.percent / HIVE_PERCENT_PRECISION :.2f}%"
            for withdraw_route in content.withdraw_routes
        }
        self.query_one("#withdraw-routes-header", Static).update("Your withdraw routes")
        self._pretty.update(withdraw_routes)
        self._pretty.display = True

    @property
    def provider(self) -> HivePowerDataProvider:
        return self.screen.query_one(HivePowerDataProvider)


class PendingPowerDownHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("Next power down", classes=ODD_CLASS_NAME)
        yield Static("Power down [HP]", classes=EVEN_CLASS_NAME)
        yield Static("Power down [VESTS]", classes=ODD_CLASS_NAME)
        yield PlaceTaker()


class PendingPowerDown(CliveCheckerboardTable):
    def __init__(self) -> None:
        super().__init__(
            Static("Current power down", id="current-power-down-title"), PendingPowerDownHeader(), dynamic=True
        )
        self._previous_next_vesting_withdrawal: datetime = datetime.min

    def create_dynamic_rows(self, content: HivePowerData) -> list[CliveCheckerboardTableRow]:
        self._previous_next_vesting_withdrawal = content.next_vesting_withdrawal

        return [
            CliveCheckerboardTableRow(
                CliveCheckerBoardTableCell(humanize_datetime(content.next_vesting_withdrawal)),
                CliveCheckerBoardTableCell(Asset.pretty_amount(content.next_power_down.hp_balance)),
                CliveCheckerBoardTableCell(Asset.pretty_amount(content.next_power_down.vests_balance)),
                CliveCheckerBoardTableCell(CliveButton("Cancel", variant="error")),
            )
        ]

    def get_no_content_available_widget(self) -> Static:
        return Static("You have no current power down process", id="no-current-power-down-info")

    @on(CliveButton.Pressed)
    def push_operation_summary_screen(self) -> None:
        self.app.push_screen(
            CancelPowerDown(self.provider.content.next_vesting_withdrawal, self.provider.content.next_power_down)
        )

    @property
    def is_anything_to_display(self) -> bool:
        return humanize_datetime(self.provider.content.next_vesting_withdrawal) != "never"

    @property
    def provider(self) -> HivePowerDataProvider:
        return self.screen.query_one(HivePowerDataProvider)

    @property
    def check_if_should_be_updated(self) -> bool:
        return self.provider.content.next_vesting_withdrawal != self._previous_next_vesting_withdrawal


class PowerDown(TabPane, OperationActionBindings):
    """TabPane with all content about power down."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: TextType) -> None:
        """
        Initialize the PowerDown tab-pane.

        Args:
        ----
        title: Title of the TabPane (will be displayed in a tab label).
        """
        super().__init__(title=title)
        self._shares_input = HPVestsAmountInput()
        self._one_withdrawal_display = Notice(
            obj_to_watch=self._shares_input.input,
            attribute_name="value",
            callback=self._calculate_one_withdrawal,
            init=False,
        )
        self._one_withdrawal_display.display = False

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield HpVestsFactor(self.provider)
            yield SectionTitle("Perform a power down (withdraw vesting)")
            with Horizontal(id="input-with-button"):
                yield self._shares_input
                yield GenerousButton(self._shares_input, self._get_shares_balance)  # type: ignore[arg-type]
            yield self._one_withdrawal_display
            yield PendingPowerDown()
            yield WithdrawRoutesDisplay()

    def _get_shares_balance(self) -> Asset.Hive | Asset.Vests:
        content = self.provider.content
        owned_balance = content.owned_balance
        delegated_balance = content.delegated_balance

        if self._shares_input.selected_asset_type is Asset.Hive:
            return owned_balance.hp_balance - delegated_balance.hp_balance
        return owned_balance.vests_balance - delegated_balance.vests_balance

    def _calculate_one_withdrawal(self) -> str:
        """The withdrawal is divided into 13 parts - calculate and inform the user of the amount of one of them."""
        shares_input = self._shares_input.value_or_none()

        if shares_input is None:
            self._one_withdrawal_display.display = False
            return ""

        one_withdrawal = shares_input / 13
        self._one_withdrawal_display.display = True

        asset = f"{Asset.pretty_amount(one_withdrawal)} {'VESTS' if isinstance(one_withdrawal, Asset.Vests) else 'HP'}"
        return f"The withdrawal will be divided into 13 parts, one of which is: {asset}"

    @on(CurrencySelectorHpVests.Changed)
    def shares_type_changed(self) -> None:
        """Clear input when shares type was changed and hide factor display when vests selected."""
        self._shares_input.input.clear()

        hp_vests_factor = self.query_one(HpVestsFactor)
        if self._shares_input.selected_asset_type is Asset.Vests:
            hp_vests_factor.display = False
            return
        hp_vests_factor.display = True

    def _create_operation(self) -> WithdrawVestingOperation | None:
        asset = self._shares_input.value_or_none()

        if asset is None:
            return None

        if isinstance(asset, Asset.Hive):
            # If the user has passed an amount in `HP` - convert it to `VESTS`. The operation is performed using VESTS.
            asset = hive_to_vests(asset, self.provider.content.gdpo)

        return WithdrawVestingOperation(account=self.working_account, vesting_shares=asset)

    @property
    def provider(self) -> HivePowerDataProvider:
        return self.screen.query_one(HivePowerDataProvider)

    @property
    def working_account(self) -> str:
        return self.app.world.profile_data.working_account.name
