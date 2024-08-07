from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.events import ScreenSuspend

from clive.__private.ui.account_list_management.common.switch_working_account.switch_working_account_container import (
    SwitchWorkingAccountContainer,
)
from clive.__private.ui.account_list_management.known_accounts import KnownAccounts
from clive.__private.ui.account_list_management.tracked_accounts import TrackedAccounts
from clive.__private.ui.account_list_management.working_account import WorkingAccount
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.clive_tabbed_content import CliveTabbedContent

if TYPE_CHECKING:
    from textual.app import ComposeResult


class AccountListManagement(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]
    BIG_TITLE = "configuration"
    SUBTITLE = "accounts management"

    def create_main_panel(self) -> ComposeResult:
        with CliveTabbedContent():
            yield TrackedAccounts()
            yield WorkingAccount()
            yield KnownAccounts()

    def on_mount(self) -> None:
        self.app.trigger_profile_data_watchers()

    @on(CliveTabbedContent.TabActivated)
    @on(ScreenSuspend)
    def _confirm_selected_working_account(self) -> None:
        self.screen.query_one(SwitchWorkingAccountContainer).confirm_selected_working_account()
