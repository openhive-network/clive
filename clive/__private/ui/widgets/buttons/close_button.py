from __future__ import annotations

from clive.__private.ui.widgets.buttons.cancel_button import CancelButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class CloseButton(CancelButton):
    class Pressed(OneLineButton.Pressed):
        """Used to identify exactly that close button was pressed."""

    def __init__(self, label: str = "Close", id_: str = "close-button") -> None:
        super().__init__(label=label, id_=id_)
