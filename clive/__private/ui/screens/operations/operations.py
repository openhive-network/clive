from __future__ import annotations

from typing import TYPE_CHECKING, cast

from textual import on
from textual.binding import Binding

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.screens.operations import Governance
from clive.__private.ui.screens.operations.bindings import TransactionSummaryBinding
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.buttons import OneLineButton
from clive.__private.ui.widgets.not_implemented_yet import NotImplementedYetButton
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section import Section

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.__private.ui.screens.operation_base_screen import OperationBaseScreen
    from clive.__private.ui.screens.operations.governance_operations.governance_operations import GovernanceTabType


class OperationButton(OneLineButton):
    def __init__(
        self, label: TextType, operation_screen: type[OperationBaseScreen], classes: str | None = None
    ) -> None:
        super().__init__(label, classes=f"operation-button {classes}")
        self._operation_screen = operation_screen

    def create_operation_screen(self) -> OperationBaseScreen:
        return self._operation_screen()


class GovernanceOperationButton(OperationButton):
    def __init__(
        self,
        label: TextType,
        governance_initial_tab: GovernanceTabType,
        classes: str | None = None,
    ) -> None:
        super().__init__(label, Governance, classes=classes)
        self._governance_initial_tab = governance_initial_tab

    def create_operation_screen(self) -> Governance:
        return cast(Governance, self._operation_screen(self._governance_initial_tab))


class Operations(CartBasedScreen, TransactionSummaryBinding):
    CSS_PATH = [
        *CartBasedScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    BINDINGS = [
        *TransactionSummaryBinding.BINDINGS,
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def create_left_panel(self) -> ComposeResult:
        from clive.__private.ui.screens.operations import HivePowerManagement, Savings, TransferToAccount

        yield BigTitle("operations")
        with ScrollablePart():
            with Section(title="Financial"):
                yield OperationButton("Transfer", TransferToAccount, "first-in-section")
                yield OperationButton("Savings", Savings)
                yield OperationButton("Hive power management", HivePowerManagement)
                yield NotImplementedYetButton("Convert")
            with Section(title="Governance"):
                yield GovernanceOperationButton("Set/Remove proxy", "proxy", "first-in-section")
                yield GovernanceOperationButton("Vote/Unvote witnesses", "witnesses")
                yield GovernanceOperationButton("Vote/Unvote proposals", "proposals")

    @on(OperationButton.Pressed, ".operation-button")
    def push_operation_screen(self, event: OperationButton.Pressed) -> None:
        button: OperationButton = event.button  # type: ignore[assignment]
        self.app.push_screen(button.create_operation_screen())
