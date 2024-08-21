from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Literal

from textual import on
from textual.binding import Binding
from textual.containers import Center, Vertical
from textual.screen import ModalScreen

from clive.__private.core.accounts.accounts import Account
from clive.__private.models import Asset
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations import HivePowerManagement, Savings, TransferToAccount
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.section import Section

if TYPE_CHECKING:
    from textual.app import ComposeResult


ActionType = Literal["transfer-to-account", "transfer-to-savings", "power-up"]


def auto_switch_working_account(widget: CliveWidget, account: str | Account) -> None:
    if widget.profile.accounts.is_account_working(account):
        return
    widget.profile.accounts.switch_working_account(account)
    widget.notify(f"Working account automatically switched to {Account.ensure_account_name(account)}")
    widget.app.trigger_profile_watchers()


class LiquidNavigationScreenContent(Vertical):
    pass


class LiquidOperationChooseButton(OneLineButton):
    def __init__(self, label: str, action: ActionType, account: Account, asset_type: type[Asset.LiquidT]) -> None:
        super().__init__(label=label)
        self._action = action
        self._account = account
        self._asset_type = asset_type

    @on(OneLineButton.Pressed)
    def push_liquid_operation_screen(self) -> None:
        action_map: dict[ActionType, Callable[[], None]] = {
            "transfer-to-account": self._push_transfer_to_account_screen,
            "transfer-to-savings": self._push_transfer_to_savings_screen,
            "power-up": self._push_power_up_screen,
        }

        auto_switch_working_account(self, self._account)
        action_map[self._action]()

    def _push_transfer_to_account_screen(self) -> None:
        self.app.push_screen(TransferToAccount(default_asset_selected=self._asset_type))

    def _push_transfer_to_savings_screen(self) -> None:
        self.app.push_screen(Savings(initial_tab="transfer-tab", default_asset_selected=self._asset_type))

    def _push_power_up_screen(self) -> None:
        self.app.push_screen(HivePowerManagement())


class LiquidNavigationScreen(ModalScreen[None], CliveWidget):
    CSS_PATH = [get_relative_css_path(__file__)]
    BINDINGS = [Binding("escape", "cancel", "Quit")]

    def __init__(self, account: Account, asset_type: type[Asset.LiquidT]) -> None:
        super().__init__()
        self._account = account
        self._asset_type = asset_type

    def compose(self) -> ComposeResult:
        content = LiquidNavigationScreenContent()
        content.border_title = f"Choose liquid operation to perform on {Asset.get_symbol(self._asset_type)}"

        with content:
            with Center(), Section():
                yield self._create_liquid_operation_choose_button("Transfer to account", "transfer-to-account")
                yield self._create_liquid_operation_choose_button("Transfer to savings", "transfer-to-savings")
                yield self._create_liquid_operation_choose_button("Power up", "power-up")
            with Center():
                yield OneLineButton("Cancel", id_="cancel-button", variant="error")

    @on(OneLineButton.Pressed, "#cancel-button")
    def action_cancel(self) -> None:
        self.app.pop_screen()

    def _create_liquid_operation_choose_button(self, label: str, action: ActionType) -> LiquidOperationChooseButton:
        return LiquidOperationChooseButton(label, action, self._account, self._asset_type)
