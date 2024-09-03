from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.binding import Binding

from clive.__private.ui.account_details.alarms.alarms import Alarms
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.clive_basic import CliveTabbedContent
from clive.__private.ui.widgets.not_implemented_yet import NotImplementedYetTabPane

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.accounts.accounts import TrackedAccount

OPERATIONS_TAB_PANE_TITLE: Final[str] = "Operations"
BALANCES_TAB_PANE_TITLE: Final[str] = "Balances"


class AccountDetails(BaseScreen):
    BIG_TITLE = "account details"

    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]

    def __init__(self, account: TrackedAccount) -> None:
        super().__init__()
        self._account = account
        self.subtitle = f"for the {account.name} account"

    def create_main_panel(self) -> ComposeResult:
        with CliveTabbedContent():
            yield Alarms(self._account)
            yield NotImplementedYetTabPane(OPERATIONS_TAB_PANE_TITLE)
            yield NotImplementedYetTabPane(BALANCES_TAB_PANE_TITLE)
