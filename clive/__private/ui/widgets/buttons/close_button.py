from __future__ import annotations

from clive.__private.ui.widgets.buttons.cancel_button import CancelOneLineButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class CloseOneLineButton(CancelOneLineButton):
    class Pressed(OneLineButton.Pressed):
        """Used to identify exactly that CloseOneLineButton was pressed."""

    def __init__(self, label: str = "Close", id_: str = "close-button") -> None:
        super().__init__(label=label, id_=id_)
