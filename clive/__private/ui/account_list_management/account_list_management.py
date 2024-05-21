from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.binding import Binding

from clive.__private.ui.account_list_management.known_accounts import KnownAccounts
from clive.__private.ui.account_list_management.watched_accounts import WatchedAccounts
from clive.__private.ui.account_list_management.working_account import WorkingAccount
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.clive_tabbed_content import CliveTabbedContent
from clive.__private.ui.widgets.location_indicator import LocationIndicator

if TYPE_CHECKING:
    from textual.app import ComposeResult

WATCHED_ACCOUNTS_TAB_LABEL: Final[str] = "Watched accounts"
KNOWN_ACCOUNTS_TAB_LABEL: Final[str] = "Known accounts"
WORKING_ACCOUNT_TAB_LABEL: Final[str] = "Working account"


class AccountListManagement(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]

    def create_main_panel(self) -> ComposeResult:
        yield LocationIndicator("configuration", "accounts management")
        with CliveTabbedContent():
            yield WatchedAccounts(WATCHED_ACCOUNTS_TAB_LABEL)
            yield KnownAccounts(KNOWN_ACCOUNTS_TAB_LABEL)
            yield WorkingAccount(WORKING_ACCOUNT_TAB_LABEL)

    def on_mount(self) -> None:
        self.app.trigger_profile_data_watchers()
