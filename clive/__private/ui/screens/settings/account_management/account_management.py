from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.screens.settings.account_management.bad_accounts import BadAccounts
from clive.__private.ui.screens.settings.account_management.known_accounts import KnownAccounts
from clive.__private.ui.screens.settings.account_management.tracked_accounts import TrackedAccounts
from clive.__private.ui.widgets.clive_basic import CliveTabbedContent

if TYPE_CHECKING:
    from textual.app import ComposeResult


class AccountManagement(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]
    BIG_TITLE = "Settings"
    SUBTITLE = "accounts management"

    def create_main_panel(self) -> ComposeResult:
        with CliveTabbedContent():
            yield TrackedAccounts()
            yield KnownAccounts()
            yield BadAccounts()

    def on_mount(self) -> None:
        self.app.trigger_profile_watchers()
