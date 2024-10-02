from __future__ import annotations

from clive.__private.ui.widgets.buttons import CliveButton


class RemoveButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Message send when RemoveButton is pressed."""

    def __init__(self) -> None:
        super().__init__("X", id_="remove-button", variant="error")
