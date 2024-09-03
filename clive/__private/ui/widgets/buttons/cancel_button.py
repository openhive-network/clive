from __future__ import annotations

from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class CancelButton(OneLineButton):
    class Pressed(OneLineButton.Pressed):
        """Used to identify exactly that cancel button was pressed."""

    def __init__(self, label: str = "Cancel", id_: str = "cancel-button") -> None:
        super().__init__(label, variant="error", id_=id_)
