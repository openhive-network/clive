from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from textual import on
from textual.containers import Center

from clive.__private.core.accounts.accounts import Account
from clive.__private.models.asset import Asset
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.dialogs.clive_base_dialogs import AutoDismissDialog, CliveInfoDialog
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.operations import HivePowerManagement, Savings, TransferToAccount
from clive.__private.ui.widgets.buttons import OneLineButton
from clive.__private.ui.widgets.section import Section

if TYPE_CHECKING:
    from collections.abc import Callable

    from textual.app import ComposeResult

    from clive.__private.ui.clive_widget import CliveWidget

ActionType = Literal["transfer-to-account", "transfer-to-savings", "power-up"]


def auto_switch_working_account(widget: CliveWidget, account: str | Account) -> None:
    if widget.profile.accounts.is_account_working(account):
        return
    widget.profile.accounts.switch_working_account(account)
    widget.notify(f"Working account automatically switched to {Account.ensure_account_name(account)}")
    widget.app.trigger_profile_watchers()


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


class LiquidNavigationDialog(AutoDismissDialog, CliveInfoDialog):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self, account: Account, asset_type: type[Asset.LiquidT]) -> None:
        super().__init__(border_title=f"Choose liquid operation to perform on {Asset.get_symbol(asset_type)}")
        self._account = account
        self._asset_type = asset_type

    def create_dialog_content(self) -> ComposeResult:
        with Center(), Section():
            yield self._create_liquid_operation_choose_button("Transfer to account", "transfer-to-account")
            yield self._create_liquid_operation_choose_button("Transfer to savings", "transfer-to-savings")
            if self._asset_type == Asset.Hive:
                yield self._create_liquid_operation_choose_button("Power up", "power-up")

    def _create_liquid_operation_choose_button(self, label: str, action: ActionType) -> LiquidOperationChooseButton:
        return LiquidOperationChooseButton(label, action, self._account, self._asset_type)
