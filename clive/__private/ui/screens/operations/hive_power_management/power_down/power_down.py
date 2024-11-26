from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Horizontal
from textual.widgets import Pretty, Static, TabPane

from clive.__private.core.constants.tui.class_names import CLIVE_EVEN_COLUMN_CLASS_NAME, CLIVE_ODD_COLUMN_CLASS_NAME
from clive.__private.core.ensure_vests import ensure_vests
from clive.__private.core.formatters.humanize import humanize_datetime, humanize_percent
from clive.__private.core.percent_conversions import hive_percent_to_percent
from clive.__private.models import Asset
from clive.__private.models.schemas import WithdrawVestingOperation
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.data_providers.hive_power_data_provider import HivePowerDataProvider
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.not_updated_yet import NotUpdatedYet
from clive.__private.ui.screens.operations.bindings.operation_action_bindings import OperationActionBindings
from clive.__private.ui.screens.operations.operation_summary.cancel_power_down import CancelPowerDown
from clive.__private.ui.widgets.buttons import (
    AddToCartButton,
    CancelOneLineButton,
    FinalizeTransactionButton,
    GenerousButton,
)
from clive.__private.ui.widgets.clive_basic import (
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.currency_selector.currency_selector_hp_vests import CurrencySelectorHpVests
from clive.__private.ui.widgets.inputs.hp_vests_amount_input import HPVestsAmountInput
from clive.__private.ui.widgets.notice import Notice
from clive.__private.ui.widgets.place_taker import PlaceTaker
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section import Section

if TYPE_CHECKING:
    from datetime import datetime

    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.__private.core.commands.data_retrieval.hive_power_data import HivePowerData


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
        self.watch(self.provider, "_content", self._update_withdraw_routes)

    def _update_withdraw_routes(self, content: HivePowerData | None) -> None:
        """Update withdraw routes pretty widget."""
        if content is None:  # data not received yet
            return

        if not content.withdraw_routes:
            self.query_exactly_one("#withdraw-routes-header", Static).update("You have no withdraw routes")
            self._pretty.display = False
            return

        withdraw_routes = {
            withdraw_route.to_account: humanize_percent(hive_percent_to_percent(withdraw_route.percent))
            for withdraw_route in content.withdraw_routes
        }
        self.query_exactly_one("#withdraw-routes-header", Static).update("Your withdraw routes")
        self._pretty.update(withdraw_routes)
        self._pretty.display = True

    @property
    def provider(self) -> HivePowerDataProvider:
        return self.screen.query_exactly_one(HivePowerDataProvider)


class PendingPowerDownHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("Next power down", classes=CLIVE_ODD_COLUMN_CLASS_NAME)
        yield Static("Power down [HP]", classes=CLIVE_EVEN_COLUMN_CLASS_NAME)
        yield Static("Power down [VESTS]", classes=CLIVE_ODD_COLUMN_CLASS_NAME)
        yield PlaceTaker()


class PendingPowerDown(CliveCheckerboardTable):
    ATTRIBUTE_TO_WATCH = "_content"
    NO_CONTENT_TEXT = "You have no pending power down"

    def __init__(self) -> None:
        super().__init__(header=PendingPowerDownHeader(), title="Current power down")
        self._previous_next_vesting_withdrawal: datetime | NotUpdatedYet = NotUpdatedYet()

    def create_dynamic_rows(self, content: HivePowerData) -> list[CliveCheckerboardTableRow]:
        return [
            CliveCheckerboardTableRow(
                CliveCheckerBoardTableCell(humanize_datetime(content.next_vesting_withdrawal)),
                CliveCheckerBoardTableCell(Asset.pretty_amount(content.next_power_down.hp_balance)),
                CliveCheckerBoardTableCell(Asset.pretty_amount(content.next_power_down.vests_balance)),
                CliveCheckerBoardTableCell(CancelOneLineButton()),
            )
        ]

    @on(CancelOneLineButton.Pressed)
    def push_operation_summary_screen(self) -> None:
        self.app.push_screen(
            CancelPowerDown(
                self.object_to_watch.content.next_vesting_withdrawal, self.object_to_watch.content.next_power_down
            )
        )

    def is_anything_to_display(self, content: HivePowerData) -> bool:
        return humanize_datetime(content.next_vesting_withdrawal) != "never"

    @property
    def object_to_watch(self) -> HivePowerDataProvider:
        return self.screen.query_exactly_one(HivePowerDataProvider)

    def check_if_should_be_updated(self, content: HivePowerData) -> bool:
        return content.next_vesting_withdrawal != self._previous_next_vesting_withdrawal

    def update_previous_state(self, content: HivePowerData) -> None:
        self._previous_next_vesting_withdrawal = content.next_vesting_withdrawal


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
            with Section("Perform a power down (withdraw vesting)"):
                with Horizontal():
                    yield self._shares_input
                    yield GenerousButton(self._shares_input, self._get_shares_balance)  # type: ignore[arg-type]
                with Horizontal(classes="horizontal-buttons"):
                    yield AddToCartButton()
                    yield FinalizeTransactionButton()
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
        """Calculate and inform the user of the amount of one withdrawal, because it's divided into 13 parts."""
        if self._shares_input.is_empty:
            # validation shouldn't be triggered when this input is cleared when adding to cart
            self._one_withdrawal_display.display = False
            return ""

        value = self._shares_input.value_or_none()
        if value is None:
            self._one_withdrawal_display.display = False
            return ""

        one_withdrawal = value / 13
        self._one_withdrawal_display.display = True

        asset = f"{Asset.pretty_amount(one_withdrawal)} {'VESTS' if isinstance(one_withdrawal, Asset.Vests) else 'HP'}"
        return f"The withdrawal will be divided into 13 parts, one of which is: {asset}"

    @on(CurrencySelectorHpVests.Changed)
    def shares_type_changed(self) -> None:
        self._one_withdrawal_display.force_dynamic_update()

    def _create_operation(self) -> WithdrawVestingOperation | None:
        asset = self._shares_input.value_or_none()

        if asset is None:
            return None

        # If the user has passed an amount in `HP` - convert it to `VESTS`. The operation is performed using VESTS.
        asset = ensure_vests(asset, self.provider.content.gdpo)

        return WithdrawVestingOperation(account=self.profile.accounts.working.name, vesting_shares=asset)

    @property
    def provider(self) -> HivePowerDataProvider:
        return self.screen.query_exactly_one(HivePowerDataProvider)
