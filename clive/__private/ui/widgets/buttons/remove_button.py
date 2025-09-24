from __future__ import annotations

from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class RemoveButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Message send when RemoveButton is pressed."""

    def __init__(self) -> None:
        super().__init__("X", id_="remove-button", variant="error")


class RemoveOneLineButton(OneLineButton, RemoveButton):
    class Pressed(RemoveButton.Pressed):
        """Message sent when RemoveOneLineButton is pressed."""
