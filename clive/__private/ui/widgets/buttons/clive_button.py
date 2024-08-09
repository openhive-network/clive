from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from textual.binding import Binding
from textual.css._error_tools import friendly_list
from textual.widgets import Button
from textual.widgets._button import ButtonVariant, InvalidButtonVariant

from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from rich.text import TextType

CliveButtonVariant = ButtonVariant | Literal["success-transparent", "grey-darken", "grey-lighten"]
_CLIVE_VALID_BUTTON_VARIANTS = {
    "default",
    "primary",
    "success",
    "warning",
    "error",
    "success-transparent",
    "grey-darken",
    "grey-lighten",
}


class CliveButton(Button, CliveWidget):
    """A regular Textual button which also displays "enter" action binding."""

    DEFAULT_CSS = """
    CliveButton {
        &.-success-transparent {
            background: $panel;
            color: green;

            &:hover {
                background: $background-darken-1;
            }
        }

        &.-grey-lighten {
            background: $panel-lighten-2;

            &:hover {
                background: $background-darken-1;
            }
        }

        &.-grey-darken {
            background: $panel-lighten-1;

            &:hover {
                background: $background-darken-1;
            }
        }
    }
    """

    def __init__(
        self,
        label: TextType | None = None,
        variant: CliveButtonVariant = "primary",
        *,
        id_: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(label=label, variant=variant, id=id_, classes=classes, disabled=disabled)  # type: ignore[arg-type]

    def on_focus(self) -> None:
        self.bind(Binding("enter", "press", str(self.label)))

    def validate_variant(self, variant: str) -> str:
        try:
            return super().validate_variant(variant)
        except InvalidButtonVariant:
            pass

        if variant not in _CLIVE_VALID_BUTTON_VARIANTS:
            raise InvalidButtonVariant(f"Valid button variants are {friendly_list(_CLIVE_VALID_BUTTON_VARIANTS)}")
        return variant
