from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.binding import Binding
from textual.widgets import TabPane

from clive.__private.ui.alarms_representation.alarms import Alarms
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.clive_tabbed_content import CliveTabbedContent

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.storage.accounts import Account

ALARMS_TAB_PANE_TITLE: Final[str] = "Alarms"
OPERATIONS_TAB_PANE_TITLE: Final[str] = "Operations"
BALANCES_TAB_PANE_TITLE: Final[str] = "Balances"


class AccountDetails(BaseScreen):
    BIG_TITLE = "account details"

    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]

    def __init__(self, account: Account) -> None:
        super().__init__()
        self._account = account
        self.subtitle = f"for the {account.name} account"

    def create_main_panel(self) -> ComposeResult:
        with CliveTabbedContent():
            yield Alarms(ALARMS_TAB_PANE_TITLE, self._account)
            yield TabPane(OPERATIONS_TAB_PANE_TITLE)
            yield TabPane(BALANCES_TAB_PANE_TITLE)
