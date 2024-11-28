from __future__ import annotations

from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class RefreshButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Message sent when RefreshButton is pressed."""

    def __init__(self) -> None:
        super().__init__("Refresh", id_="button-refresh")


class RefreshOneLineButton(OneLineButton, RefreshButton):
    class Pressed(RefreshButton.Pressed):
        """Message sent when RefreshOneLineButton is pressed."""
