from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import Label

from clive.__private.ui.widgets.clive_checkerboard_table import EVEN_CLASS_NAME, ODD_CLASS_NAME

if TYPE_CHECKING:
    from textual.app import ComposeResult


class AccountsTableHeader(Horizontal):
    DEFAULT_CSS = """
    AccountsTableHeader {
      height: 1;

      Label {
        width: 1fr;
        text-style: bold;
      }
    }
    """

    def __init__(self, account_column_name: str = "Name"):
        super().__init__()
        self._account_column_name = account_column_name

    def compose(self) -> ComposeResult:
        yield Label(self._account_column_name, classes=ODD_CLASS_NAME)
        yield Label("Action", classes=EVEN_CLASS_NAME)
