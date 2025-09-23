from __future__ import annotations

from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class ModifyButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that ModifyButton button was pressed."""

    def __init__(self, label: str = "Modify", id_: str = "modify-button") -> None:
        super().__init__(label, variant="success", id_=id_)


class ModifyOneLineButton(OneLineButton, ModifyButton):
    class Pressed(ModifyButton.Pressed):
        """Used to identify exactly that ModifyOneLineButton was pressed."""
