from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container, Horizontal
from textual.widgets import Static

from clive.__private.core.constants.tui.class_names import CLIVE_EVEN_COLUMN_CLASS_NAME, CLIVE_ODD_COLUMN_CLASS_NAME
from clive.__private.ui.screens.account_details.authority.filter_authority import (
    FilterAuthority,
    FilterAuthorityExtended,
)

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.ui.widgets.buttons.clive_button import CliveButton


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


class TopContainer(Horizontal):
    """
    Container with FilterAuthority widget and additional action button.

    To use version with extended filtering (by accounts), provide an account to the init method.

    Attributes:
        DEFAULT_CSS: The default CSS styling for the container.

    Args:
        action_button: The button that will be placed next to the filter authority widget.
        account: The account that will be initially selected in the filter authority widget.
    """

    DEFAULT_CSS = """
    TopContainer {
        margin: 1 0;
        width: auto;
        height: auto;

        #button-container {
            margin: 2 0 0 2;
            padding-right: 1;
            width: 1fr;
            height: auto;

            CliveButton {
                min-width: 1fr;
            }
        }
    }
    """

    def __init__(
        self,
        *,
        action_button: CliveButton,
        account: TrackedAccount | None = None,
    ) -> None:
        super().__init__()
        self._account = account
        self._action_button = action_button

    def compose(self) -> ComposeResult:
        filter_widget = FilterAuthorityExtended(self._account) if self._account else FilterAuthority()
        yield filter_widget
        with Container(id="button-container"):
            yield self._action_button
