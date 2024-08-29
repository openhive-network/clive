from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.widgets import TabPane

from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.switch_working_account_container import (
    SwitchWorkingAccountContainer,
)

if TYPE_CHECKING:
    from textual.app import ComposeResult


class SwitchWorkingAccount(TabPane, CliveWidget):
    """TabPane used to modify the working account."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)
    TITLE: Final[str] = "Switch working account"

    def __init__(self) -> None:
        super().__init__(self.TITLE)

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield SwitchWorkingAccountContainer()
