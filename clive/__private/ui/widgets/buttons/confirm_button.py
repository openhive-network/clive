from __future__ import annotations

from typing import ClassVar

from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton


class ConfirmButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that ConfirmButton button was pressed."""

    DEFAULT_LABEL: ClassVar[str] = "Confirm"

    def __init__(self, label: str = DEFAULT_LABEL, id_: str = "confirm-button") -> None:
        super().__init__(label, variant="success", id_=id_)


class ConfirmOneLineButton(OneLineButton, ConfirmButton):
    class Pressed(ConfirmButton.Pressed):
        """Used to identify exactly that ConfirmOneLineButton was pressed."""
