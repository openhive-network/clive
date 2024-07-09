from __future__ import annotations

from clive.__private.ui.widgets.buttons.cancel_button import CancelButton


class CloseButton(CancelButton):
    def __init__(self, label: str = "Close", id_: str = "close-button") -> None:
        super().__init__(label=label, id_=id_)
