from __future__ import annotations

from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class CloseButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that CloseButton was pressed."""

    def __init__(self, label: str = "Close", id_: str = "close-button") -> None:
        super().__init__(label=label, variant="error", id_=id_)


class CloseOneLineButton(OneLineButton, CloseButton):
    class Pressed(CloseButton.Pressed):
        """Used to identify exactly that CloseOneLineButton was pressed."""
