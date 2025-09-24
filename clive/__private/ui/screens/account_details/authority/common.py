from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import Static

from clive.__private.core.constants.tui.class_names import CLIVE_EVEN_COLUMN_CLASS_NAME, CLIVE_ODD_COLUMN_CLASS_NAME

if TYPE_CHECKING:
    from textual.app import ComposeResult


class AuthorityHeader(Horizontal):
    DEFAULT_CSS = """
    AuthorityHeader {
        height: 1;

        Static {
          content-align: center middle;
        }
    }
    """

    def __init__(self, *, last_column_header_title: str, memo_header: bool = False) -> None:
        super().__init__()
        self._memo_header = memo_header
        self._last_column_header_title = last_column_header_title

    def compose(self) -> ComposeResult:
        if not self._memo_header:
            yield Static("Key / Account", classes=f"{CLIVE_ODD_COLUMN_CLASS_NAME} key-or-account")
            yield Static("Weight", classes=f"{CLIVE_EVEN_COLUMN_CLASS_NAME} weight")
            yield Static(self._last_column_header_title, classes=f"{CLIVE_ODD_COLUMN_CLASS_NAME} action")
        else:
            yield Static("Key", classes=f"{CLIVE_ODD_COLUMN_CLASS_NAME} memo-key")
            yield Static(self._last_column_header_title, classes=f"{CLIVE_EVEN_COLUMN_CLASS_NAME} action")
