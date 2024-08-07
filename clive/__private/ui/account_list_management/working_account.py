from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.widgets import TabPane

from clive.__private.ui.account_list_management.common.switch_working_account.switch_working_account_container import (
    SwitchWorkingAccountContainer,
)
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.scrolling import ScrollablePart

if TYPE_CHECKING:
    from textual.app import ComposeResult


class WorkingAccount(TabPane, CliveWidget):
    """TabPane used to modify the working account."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)
    TITLE: Final[str] = "Switch working account"

    def __init__(self) -> None:
        super().__init__(self.TITLE)

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield SwitchWorkingAccountContainer()
