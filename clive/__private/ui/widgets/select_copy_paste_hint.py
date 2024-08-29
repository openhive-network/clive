from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.widgets import Static

from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.styling import colorize_shortcut, colorize_system_text
from clive.__private.ui.widgets.clive_basic import CliveCollapsible

if TYPE_CHECKING:
    from textual.app import ComposeResult


class SelectCopyPasteHint(CliveWidget):
    DEFAULT_CSS = """
    SelectCopyPasteHint {
        height: auto;
    }
    """

    DESCRIPTION: Final[str] = f"""\
To select some text hold {colorize_shortcut("Shift")} while you click and drag.

Copy/Paste action shortcuts depend on the environment and you may check:
  > On {colorize_system_text("Linux")}: {colorize_shortcut("Ctrl+Shift+C")} / {colorize_shortcut("Ctrl+Shift+V")}
  > On {colorize_system_text("Windows")}: {colorize_shortcut("Ctrl+C")} / {colorize_shortcut("Ctrl+V")}
If none of the above works, you may also try {colorize_shortcut("Ctrl+Insert")} / {colorize_shortcut("Shift+Insert")}.
More info can be found on the Help page.\
"""

    TITLE: Final[str] = "How to select, copy and paste text inside TUI app like Clive?"

    def compose(self) -> ComposeResult:
        with CliveCollapsible(title=self.TITLE):
            yield Static(self.DESCRIPTION)
