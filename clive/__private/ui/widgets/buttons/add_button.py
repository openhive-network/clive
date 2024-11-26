from __future__ import annotations

from typing import ClassVar

from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class AddButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that AddButton button was pressed."""

    DEFAULT_LABEL: ClassVar[str] = "Add"

    def __init__(self, label: str = DEFAULT_LABEL, id_: str = "add-button") -> None:
        super().__init__(label, variant="success", id_=id_)


class AddOneLineButton(OneLineButton, AddButton):
    class Pressed(AddButton.Pressed):
        """Used to identify exactly that AddOneLineButton was pressed."""
