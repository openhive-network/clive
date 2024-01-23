from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual import on
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.css.query import NoMatches
from textual.widgets import Checkbox, Input, Label, Static, TabPane

from clive.__private.core.formatters.humanize import humanize_datetime
from clive.__private.core.hive_to_vests import hive_to_vests
from clive.__private.ui.data_providers.hive_power_data_provider import HivePowerDataProvider
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.operations.hive_power_management.common_hive_power.hp_information_table import (
    HpInformationTable,
)
from clive.__private.ui.operations.hive_power_management.common_hive_power.hp_vests_selector import (
    CurrencySelectorHpVests,
)
from clive.__private.ui.operations.raw.set_withdraw_vesting_route.set_withdraw_vesting_route import (
    SetWithdrawVestingRoute,
)
from clive.__private.ui.operations.raw.withdraw_vesting.withdraw_vesting import WithdrawVesting
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_checkerboard_table import (
    EVEN_STYLE,
    ODD_STYLE,
    CliveCheckerboardTable,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.clive_tabbed_content import CliveTabbedContent
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.inputs.numeric_input import NumericInput
from clive.__private.ui.widgets.placeholders_constants import PERCENT_PLACEHOLDER
from clive.models import Asset

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from schemas.apis.database_api.fundaments_of_reponses import WithdrawVestingRoutesFundament as WithdrawRouteSchema


class PlaceTaker(Static):
    pass


class CurrentWithdrawalRow(CliveCheckerboardTableRow):
    """Row of the CurrentWithdrawalTable, that displays the date and amount of the next withdrawal."""

    def __init__(self) -> None:
        super().__init__()
        self._date_column = Label("", classes=ODD_STYLE)
        """next withdrawal date"""
        self._withdraw_value_column = Label("", classes=EVEN_STYLE)
        """"next withdrawal amount"""

    def create_row_columns(self) -> ComposeResult:
        yield self._date_column
        yield self._withdraw_value_column

    def on_mount(self) -> None:
        self.watch(self.provider, "_content", self._sync_withdrawal_data)

    def _sync_withdrawal_data(self) -> None:
        """If there are no pending withdrawals `never` and `0.000 / 0.0000` will be displayed."""
        try:
            if self.provider.is_content_set:
                self._date_column.update(f"{humanize_datetime(self.provider.content.next_vesting_withdrawal)}")
                self._withdraw_value_column.update(
                    f"{Asset.pretty_amount(self.provider.content.to_withdraw.hp_balance)} HP /"
                    f" {Asset.pretty_amount(self.provider.content.to_withdraw.vests_balance)} VESTS"
                )
        except NoMatches:
            pass

    @property
    def provider(self) -> HivePowerDataProvider:
        return self.app.query_one(HivePowerDataProvider)


class CurrentWithdrawalTable(CliveCheckerboardTable):
    def create_header_columns(self) -> ComposeResult:
        yield Label("Next withdrawal date", classes=f"{EVEN_STYLE} checkerboard-header-label")
        yield Label("Remains to be withdrawn", classes=f"{ODD_STYLE} checkerboard-header-label")

    def create_rows(self) -> ComposeResult:
        yield CurrentWithdrawalRow()


class WithdrawRouteCell(Vertical):
    def __init__(self, text_to_display: str, classes: str | None = None) -> None:
        """
        Initialise the withdrawal route cell.

        Args:
        ----
        text_to_display: Text to be displayed in the cell.
        classes: The CSS classes for the widget.
        """
        super().__init__(classes=classes)
        self._text_to_display = text_to_display

    def compose(self) -> ComposeResult:
        yield PlaceTaker()
        yield Label(self._text_to_display)
        yield PlaceTaker()


class WithdrawRoute(CliveCheckerboardTableRow):
    CANCEL_WITHDRAW_PERCENT: Final[int] = 0

    def __init__(self, receiver: str, percent: int, auto_vest: bool, evenness: str = "odd") -> None:
        """
        Initialize the WithdrawRoute row.

        Args:
        ----
        receiver: The receiver of the withdrawal route.
        percent: Percentage of withdrawal to be sent to receiver.
        auto_vest: Is withdrawal with auto vest or no.
        evenness: Evenness of the row.
        """
        super().__init__()
        self._receiver = receiver
        self._percent = percent
        self._auto_vest = auto_vest

        self._evenness = evenness

    def create_row_columns(self) -> ComposeResult:
        yield WithdrawRouteCell(self._receiver, classes=ODD_STYLE if self._evenness == "odd" else EVEN_STYLE)
        yield WithdrawRouteCell(str(self._percent), classes=EVEN_STYLE if self._evenness == "odd" else ODD_STYLE)
        yield WithdrawRouteCell(str(self._auto_vest), classes=ODD_STYLE if self._evenness == "odd" else EVEN_STYLE)
        yield CliveButton("Remove", classes="remove-withdraw-route-button")

    @on(CliveButton.Pressed)
    def push_operation_summary_screen(self) -> None:
        self.app.push_screen(
            SetWithdrawVestingRoute(
                receiver=self._receiver, percent=self.CANCEL_WITHDRAW_PERCENT, auto_vest=self._auto_vest, cancel=True
            )
        )


class WithdrawRoutesWrapper(Vertical):
    """Container to display withdraw routes - created to simply query, remove, create new and mount it."""

    def __init__(self, withdraw_routes: list[WithdrawRouteSchema]) -> None:
        """
        Initialize the WithdrawRoutesWrapper.

        Args:
        ----
        withdraw_routes: list of withdraw routes to display.
        """
        super().__init__()
        self._withdraw_routes = withdraw_routes

    def compose(self) -> ComposeResult:
        for evenness, withdraw_route in enumerate(self._withdraw_routes):
            yield WithdrawRoute(
                withdraw_route.to_account,
                withdraw_route.percent // 100,
                withdraw_route.auto_vest,
                "even" if evenness % 2 == 0 else "odd",
            )


class WithdrawRoutes(CliveCheckerboardTable):
    """Table with WithdrawRoutes."""

    def create_table_title(self) -> ComposeResult:
        yield Static("Current withdraw routes", id="withdraw-routes-table-title")

    def create_header_columns(self) -> ComposeResult:
        yield Static("To", classes=ODD_STYLE)
        yield Static("Percent", classes=EVEN_STYLE)
        yield Static("Auto vest", classes=ODD_STYLE)
        yield PlaceTaker()

    def on_mount(self) -> None:
        self.watch(self.provider, "_content", self._sync_withdraw_routes)

    def create_rows(self) -> ComposeResult:
        if self.withdraw_routes is not None and len(self.withdraw_routes) != 0:
            self._sync_withdraw_routes()
            return
        yield Static("You have no withdraw routes", id="withdraw-routes-info")

    def _sync_withdraw_routes(self) -> None:
        with self.app.batch_update():
            self.query(WithdrawRoutesWrapper).remove()
            if self.withdraw_routes is not None and len(self.withdraw_routes) != 0:
                self.query("#withdraw-routes-info").remove()
                self.mount(WithdrawRoutesWrapper(self.withdraw_routes))

    @property
    def withdraw_routes(self) -> list[WithdrawRouteSchema] | None:
        if not self.provider.is_content_set:
            return None
        return self.provider.content.withdraw_routes

    @property
    def provider(self) -> HivePowerDataProvider:
        return self.app.query_one(HivePowerDataProvider)


class WithdrawTabPane(TabPane, CliveWidget):
    """TabPane to make a withdrawal."""

    BINDINGS = [Binding("f2", "withdraw", "Withdraw")]

    def __init__(self, title: TextType) -> None:
        """
        Initialize the WithdrawTabPane.

        Args:
        ----
        title: Title of the TabPane (will be displayed in a tab label).
        """
        super().__init__(title=title)
        self._shares_input = NumericInput()
        self._hp_vests_selector = CurrencySelectorHpVests()
        self._instalment_display = Static("", id="withdraw-instalment-display")
        self._instalment_display.display = False

    def compose(self) -> ComposeResult:
        with Horizontal(id="withdraw-input-container"):
            yield self._shares_input
            yield self._hp_vests_selector
            yield CliveButton("All !", id_="fill-by-all-button")
        yield self._instalment_display
        yield CurrentWithdrawalTable()
        yield WithdrawRoutes()

    @on(Input.Changed)
    def calculate_one_withdrawal(self) -> None:
        """The withdrawal is divided into 13 parts - calculate and inform the user of the amount of one of them."""
        shares_input = self._shares_input.input.value
        # Do not want to report an error here - only when the user tries to make a withdrawal

        if not shares_input:
            self._instalment_display.display = False
            self._instalment_display.update("")
            return

        try:
            converted_shares = float(shares_input)  # TODO after change inputs to the new one, change this
        except ValueError:
            return

        self._instalment_display.update(
            "The withdrawal will be divided into 13 parts, one of which is: "
            f"{self._calculate_one_withdrawal_value(converted_shares)}"
        )
        self._instalment_display.display = True

    @on(CliveButton.Pressed, "#fill-by-all-button")
    def fill_input_by_all(self) -> None:
        """Fill shares_input by the entire balance of the user's HP/VESTS."""
        selected_token = self._hp_vests_selector.value.asset_cls.get_asset_information().symbol[0]  # type: ignore[union-attr]
        shares_balance = (
            Asset.pretty_amount(self.provider.content.owned_balance.hp_balance)
            if selected_token == "HIVE"
            else Asset.pretty_amount(self.provider.content.owned_balance.vests_balance)
        )
        if float(shares_balance) == 0:
            self.notify("Zero is not enough value to make power down", severity="warning")
            return

        self._shares_input.input.value = shares_balance

    @on(CurrencySelectorHpVests.Changed)
    def clear_input(self) -> None:
        """Clear input when shares type was changed."""
        self._shares_input.input.value = ""

    async def action_withdraw(self) -> None:
        """If all input parameters are correct - push the operation summary screen (WithdrawVesting)."""
        asset_input = self._shares_input.value
        if not asset_input:
            return

        converted_asset = self._hp_vests_selector.create_asset(asset_input)
        if converted_asset is None:
            return

        selected_token = self._hp_vests_selector.value.asset_cls.get_asset_information().symbol[0]  # type: ignore[union-attr]
        if selected_token == "VESTS":
            await self.app.push_screen(WithdrawVesting(converted_asset))  # type: ignore[arg-type]
            return

        # If the user has passed an amount in `HP` - convert it to `VESTS`. The operation is performed using VESTS.
        dgpo = await self.app.world.app_state.get_dynamic_global_properties()

        calculation_factor = Asset.pretty_amount(hive_to_vests(Asset.hive(1), dgpo))
        # Calculate to show the user how much VESTS is 1 HP

        hp_to_vests = hive_to_vests(converted_asset, dgpo)  # type: ignore[arg-type]
        await self.app.push_screen(WithdrawVesting(hp_to_vests, calculation_factor=calculation_factor))

    def _calculate_one_withdrawal_value(self, shares_value: float) -> str:
        selected_token = self._hp_vests_selector.value.asset_cls.get_asset_information().symbol[0]  # type: ignore[union-attr]

        if selected_token == "HIVE":
            return f"{(shares_value / 13):.3f}"
        return f"{(shares_value / 13):.6f}"

    @property
    def provider(self) -> HivePowerDataProvider:
        return self.app.query_one(HivePowerDataProvider)


class SetWithdrawRouteTabPane(TabPane, CliveWidget):
    """TabPane to set withdrawal route."""

    BINDINGS = [Binding("f2", "set_withdraw_route", "Set withdraw route")]

    def __init__(self, title: TextType) -> None:
        """
        Initialize the SetWithdrawRouteTabPane.

        Args:
        ----
        title: title of the TabPane (will be displayed in a tab label).
        """
        super().__init__(title=title)
        self._account_input = AccountNameInput()
        self._percent_input = IntegerInput(label="percent", placeholder=PERCENT_PLACEHOLDER)
        self._checkbox = Checkbox("Auto vest")

    def compose(self) -> ComposeResult:
        yield self._account_input
        yield self._percent_input
        with Container(id="container-with-checkbox"):
            yield self._checkbox
        yield WithdrawRoutes()

    def action_set_withdraw_route(self) -> None:
        """If all input parameters are correct - push the operation summary screen (SetWithdrawVestingRoute)."""
        account_name = self._account_input.value
        percent_value = self._percent_input.value
        auto_vest = self._checkbox.value

        if not account_name or not percent_value:
            return

        max_percent_value: int = 100
        min_percent_value: int = 0
        if percent_value >= max_percent_value or percent_value <= min_percent_value:
            self.notify("Percent value must be between 0 and 100 !", severity="error")
            return

        self.app.push_screen(SetWithdrawVestingRoute(account_name, percent_value, auto_vest))


WITHDRAW_TAB_LABEL: Final[str] = "Withdraw"
SET_WITHDRAW_ROUTE_TAB_LABEL: Final[str] = "Set withdraw route"


class PowerDown(TabPane, CliveWidget):
    """TabPane with all content about power down."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: TextType):
        """
        Initialize a TabPane.

        Args:
        ----
        title: Title of the TabPane (will be displayed in a tab label).
        """
        super().__init__(title=title)

    def compose(self) -> ComposeResult:
        yield HpInformationTable()
        with CliveTabbedContent():
            yield WithdrawTabPane(WITHDRAW_TAB_LABEL)
            yield SetWithdrawRouteTabPane(SET_WITHDRAW_ROUTE_TAB_LABEL)
