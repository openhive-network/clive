from __future__ import annotations

from typing import TYPE_CHECKING, Literal, cast

from textual import on
from textual.binding import Binding
from textual.containers import Center, Vertical
from textual.events import Click
from textual.screen import ModalScreen

from clive.__private.core.accounts.accounts import Account
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.section import Section

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Asset


def auto_switch_working_account(widget: CliveWidget, account: str | Account) -> None:
    if widget.profile.accounts.is_account_working(account):
        return
    widget.profile.accounts.switch_working_account(account)
    widget.notify(f"Working account automatically switched to {Account.ensure_account_name(account)}")


class LiquidNavigationScreenContent(Vertical):
    BORDER_TITLE = "Liquid operations"


class LiquidOperationChooseButton(OneLineButton):
    def __init__(
        self, label: str, operation: Literal["transfer-to-account", "transfer-to-savings", "power-up"]
    ) -> None:
        super().__init__(label=label, classes="liquid-operation-choose-button")
        self.operation = operation


class LiquidNavigationScreen(ModalScreen[None], CliveWidget):
    CSS_PATH = [get_relative_css_path(__file__)]
    BINDINGS = [Binding("escape", "cancel", "Quit")]

    def __init__(self, account: Account, asset_type: type[Asset.LiquidT]) -> None:
        super().__init__()
        self._account = account
        self._asset_type = asset_type

    def compose(self) -> ComposeResult:
        with LiquidNavigationScreenContent(), Section("Choose liquid operation to perform"), Center():
            yield LiquidOperationChooseButton("Transfer to account", operation="transfer-to-account")
            yield LiquidOperationChooseButton("Transfer to savings", operation="transfer-to-savings")
            yield LiquidOperationChooseButton("Power up", operation="power-up")
            yield OneLineButton("Cancel", id_="cancel-button", variant="error")

    @on(LiquidOperationChooseButton.Pressed, ".liquid-operation-choose-button")
    def push_liquid_operation_screen(self, event: LiquidOperationChooseButton.Pressed) -> None:
        auto_switch_working_account(self, self._account)

        button = cast(LiquidOperationChooseButton, event.button)
        match button.operation:
            case "transfer-to-account":
                from clive.__private.ui.operations.transfer_to_account.transfer_to_account import TransferToAccount

                self.app.push_screen(TransferToAccount(default_asset_selected=self._asset_type))
            case "transfer-to-savings":
                from clive.__private.ui.operations.savings_operations.savings_operations import Savings

                self.app.push_screen(Savings(initial_tab="transfer-tab", default_asset_selected=self._asset_type))
            case _:
                from clive.__private.ui.operations.hive_power_management.hive_power_management import (
                    HivePowerManagement,
                )

                self.app.push_screen(HivePowerManagement())

    @on(OneLineButton.Pressed, "#cancel-button")
    @on(Click)
    def action_cancel(self) -> None:
        self.app.pop_screen()
