from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Horizontal
from textual.widgets import Checkbox, Static, TabPane

from clive.__private.core.constants.precision import HIVE_PERCENT_PRECISION
from clive.__private.core.constants.tui.class_names import CLIVE_EVEN_COLUMN_CLASS_NAME, CLIVE_ODD_COLUMN_CLASS_NAME
from clive.__private.core.formatters.humanize import align_to_dot, humanize_bool
from clive.__private.core.percent_conversions import percent_to_hive_percent
from clive.__private.models.schemas import SetWithdrawVestingRouteOperation
from clive.__private.ui.data_providers.hive_power_data_provider import HivePowerDataProvider
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.not_updated_yet import NotUpdatedYet
from clive.__private.ui.screens.operations.bindings import OperationActionBindings
from clive.__private.ui.screens.operations.operation_summary.remove_withdraw_vesting_route import (
    RemoveWithdrawVestingRoute,
)
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton
from clive.__private.ui.widgets.clive_basic import (
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
from clive.__private.ui.widgets.inputs.percent_input import PercentInput
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section import Section

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.__private.core.commands.data_retrieval.hive_power_data import HivePowerData
    from clive.__private.models.schemas import WithdrawRoute as SchemasWithdrawRoute


class PlaceTaker(Static):
    pass


class WithdrawRoutesHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("To", classes=CLIVE_ODD_COLUMN_CLASS_NAME)
        yield Static("Percent", classes=CLIVE_EVEN_COLUMN_CLASS_NAME)
        yield Static("Auto vest", classes=CLIVE_ODD_COLUMN_CLASS_NAME)
        yield PlaceTaker()


class WithdrawRoute(CliveCheckerboardTableRow):
    """Row of the `WithdrawRoutesTable`."""

    def __init__(self, withdraw_route: SchemasWithdrawRoute, aligned_percent: str) -> None:
        super().__init__(
            CliveCheckerBoardTableCell(withdraw_route.to_account),
            CliveCheckerBoardTableCell(aligned_percent),
            CliveCheckerBoardTableCell(humanize_bool(withdraw_route.auto_vest)),
            CliveCheckerBoardTableCell(OneLineButton("Remove", id_="remove-withdraw-route-button", variant="error")),
        )
        self._withdraw_route = withdraw_route

    @on(CliveButton.Pressed, "#remove-withdraw-route-button")
    def push_operation_summary_screen(self) -> None:
        self.app.push_screen(RemoveWithdrawVestingRoute(self._withdraw_route))


class WithdrawRoutesTable(CliveCheckerboardTable):
    """Table with WithdrawRoutes."""

    ATTRIBUTE_TO_WATCH = "_content"

    def __init__(self) -> None:
        super().__init__(header=WithdrawRoutesHeader(), title="Current withdraw routes")
        self._previous_withdraw_routes: list[SchemasWithdrawRoute] | NotUpdatedYet = NotUpdatedYet()

    def create_dynamic_rows(self, content: HivePowerData) -> list[WithdrawRoute]:
        percents_to_align = [
            f"{withdraw_route.percent / HIVE_PERCENT_PRECISION :.2f} %" for withdraw_route in content.withdraw_routes
        ]
        aligned_percents = align_to_dot(*percents_to_align)

        return [
            WithdrawRoute(withdraw_route, aligned_percent)
            for withdraw_route, aligned_percent in zip(content.withdraw_routes, aligned_percents, strict=True)
        ]

    def get_no_content_available_widget(self) -> Static:
        return NoContentAvailable("You have no withdraw routes")

    @property
    def object_to_watch(self) -> HivePowerDataProvider:
        return self.screen.query_one(HivePowerDataProvider)

    def check_if_should_be_updated(self, content: HivePowerData) -> bool:
        return content.withdraw_routes != self._previous_withdraw_routes

    def is_anything_to_display(self, content: HivePowerData) -> bool:
        return len(content.withdraw_routes) != 0

    def update_previous_state(self, content: HivePowerData) -> None:
        self._previous_withdraw_routes = content.withdraw_routes


class WithdrawRoutes(TabPane, OperationActionBindings):
    """TabPane with all content about setting withdraw routes."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: TextType) -> None:
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
            with Section("Set withdraw route"):
                yield self._account_input
                with Horizontal(id="input-with-checkbox"):
                    yield self._percent_input
                    yield self._auto_vest_checkbox
            yield WithdrawRoutesTable()

    def _create_operation(self) -> SetWithdrawVestingRouteOperation | None:
        if not CliveValidatedInput.validate_many(self._account_input, self._percent_input):
            return None

        return SetWithdrawVestingRouteOperation(
            from_account=self.profile.accounts.working.name,
            to_account=self._account_input.value_or_error,
            percent=percent_to_hive_percent(self._percent_input.value_or_error),
            auto_vest=self._auto_vest_checkbox.value,
        )
