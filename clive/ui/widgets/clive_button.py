from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Button

from clive.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.widgets._button import ButtonVariant


class CliveButton(Button, CliveWidget):
    """A regular Textual button which also displays "enter" action binding."""

    def __init__(
        self,
        label: TextType | None = None,
        variant: ButtonVariant = "default",
        *,
        id_: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(label=label, variant=variant, id=id_, classes=classes, disabled=disabled)

    def on_focus(self) -> None:
        self.bind(Binding("enter", "press", str(self.label)))
