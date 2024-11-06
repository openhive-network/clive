from __future__ import annotations

from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class CancelButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Message sent when CancelButton is pressed."""

    def __init__(self, label: str = "Cancel", id_: str = "cancel-button") -> None:
        super().__init__(label, variant="error", id_=id_)


class CancelOneLineButton(OneLineButton, CancelButton):
    class Pressed(CancelButton.Pressed):
        """Message sent when CancelOneLineButton is pressed."""
