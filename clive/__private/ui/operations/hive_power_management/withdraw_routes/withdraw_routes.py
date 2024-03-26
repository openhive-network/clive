from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Horizontal, Vertical
from textual.widgets import Checkbox, Static, TabPane

from clive.__private.core.constants import HIVE_PERCENT_PRECISION
from clive.__private.core.formatters.humanize import humanize_bool
from clive.__private.ui.data_providers.hive_power_data_provider import HivePowerDataProvider
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.operations.bindings import OperationActionBindings
from clive.__private.ui.operations.operation_summary.remove_withdraw_vesting_route import RemoveWithdrawVestingRoute
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_checkerboard_table import (
    EVEN_CLASS_NAME,
    ODD_CLASS_NAME,
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
from clive.__private.ui.widgets.inputs.percent_input import PercentInput
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section_title import SectionTitle
from schemas.operations import SetWithdrawVestingRouteOperation

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.__private.core.commands.data_retrieval.hive_power_data import HivePowerData
    from clive.models.aliased import WithdrawRouteSchema


class PlaceTaker(Static):
    pass


class WithdrawRoutesHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("To", classes=ODD_CLASS_NAME)
        yield Static("Percent", classes=EVEN_CLASS_NAME)
        yield Static("Auto vest", classes=ODD_CLASS_NAME)
        yield PlaceTaker()


class WithdrawRoute(CliveCheckerboardTableRow):
    """Row of the `WithdrawRoutesTable`."""

    def __init__(self, withdraw_route: WithdrawRouteSchema) -> None:
        super().__init__(
            CliveCheckerBoardTableCell(withdraw_route.to_account),
            CliveCheckerBoardTableCell(f"{withdraw_route.percent / HIVE_PERCENT_PRECISION :.2f} %"),
            CliveCheckerBoardTableCell(humanize_bool(withdraw_route.auto_vest)),
            CliveCheckerBoardTableCell(CliveButton("Remove", id_="remove-withdraw-route-button", variant="error")),
        )
        self._withdraw_route = withdraw_route

    @on(CliveButton.Pressed, "#remove-withdraw-route-button")
    def push_operation_summary_screen(self) -> None:
        self.app.push_screen(RemoveWithdrawVestingRoute(self._withdraw_route))


class WithdrawRoutesTable(CliveCheckerboardTable):
    """Table with WithdrawRoutes."""

    ATTRIBUTE_TO_WATCH = "_content"

    def __init__(self) -> None:
        super().__init__(
            Static("Current withdraw routes", id="withdraw-routes-table-title"),
            WithdrawRoutesHeader(),
        )
        self._previous_withdraw_routes: list[WithdrawRouteSchema] | None = None

    def create_dynamic_rows(self, content: HivePowerData) -> list[WithdrawRoute]:
        self._previous_withdraw_routes = content.withdraw_routes

        return [WithdrawRoute(withdraw_route) for withdraw_route in content.withdraw_routes]

    def get_no_content_available_widget(self) -> Static:
        return Static("You have no withdraw routes", id="no-withdraw-routes-info")

    @property
    def object_to_watch(self) -> HivePowerDataProvider:
        return self.screen.query_one(HivePowerDataProvider)

    @property
    def check_if_should_be_updated(self) -> bool:
        return self.object_to_watch.content.withdraw_routes != self._previous_withdraw_routes

    @property
    def is_anything_to_display(self) -> bool:
        return len(self.object_to_watch.content.withdraw_routes) != 0

    @property
    def working_account(self) -> str:
        return self.app.world.profile_data.working_account.name


class WithdrawRoutes(TabPane, OperationActionBindings):
    """TabPane with all content about setting withdraw routes."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: TextType):
        """
        Initialize a TabPane.

        Args:
        ----
        title: Title of the TabPane (will be displayed in a tab label).
        """
        super().__init__(title=title)
        self._account_input = AccountNameInput()
        self._percent_input = PercentInput()
        self._auto_vest_checkbox = Checkbox("Auto vest")

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield SectionTitle("Set withdraw route")
            with Vertical(id="inputs-container"):
                yield self._account_input
                with Horizontal(id="input-with-checkbox"):
                    yield self._percent_input
                    yield self._auto_vest_checkbox
            yield WithdrawRoutesTable()

    def _create_operation(self) -> SetWithdrawVestingRouteOperation | None:
        if not CliveValidatedInput.validate_many(self._account_input, self._percent_input):
            return None

        return SetWithdrawVestingRouteOperation(
            from_account=self.working_account,
            to_account=self._account_input.value_or_error,
            percent=self._percent_input.value_or_error * HIVE_PERCENT_PRECISION,
            auto_vest=self._auto_vest_checkbox.value,
        )

    @property
    def working_account(self) -> str:
        return self.app.world.profile_data.working_account.name
