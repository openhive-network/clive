from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton

if TYPE_CHECKING:
    from clive.__private.ui.bindings.clive_binding import CliveBinding


class EditButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Message sent when EditButton is pressed."""

    def __init__(self, label: str = "Edit", *, binding: CliveBinding | None = None, id_: str = "button-edit") -> None:
        super().__init__(label, binding=binding, id_=id_)


class EditOneLineButton(OneLineButton, EditButton):
    class Pressed(EditButton.Pressed):
        """Message sent when EditOneLineButton is pressed."""
