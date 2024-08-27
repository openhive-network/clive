from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from rich.text import Text
from textual.binding import Binding
from textual.widgets import Button
from textual.widgets._button import ButtonVariant

from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.reactive import reactive

CliveButtonVariant = Literal[
    "loading-variant", "success-on-transparent", "error-on-transparent", "grey-darken", "grey-lighten", ButtonVariant
]


class CliveButton(Button, CliveWidget):
    """A regular Textual button which also displays "enter" action binding."""

    DEFAULT_CSS = """
    CliveButton {
        &.-loading-variant {
            background: $panel-lighten-1;

            &:hover {
                background: rgba(0, 0, 0, 0.2);
            }
        }

        &.-success-on-transparent {
            background: rgba(0, 0, 0, 0);
            color: $success-darken-3;

            &:hover {
                background: rgba(0, 0, 0, 0.2);
            }
        }

        &.-error-on-transparent {
            background: rgba(0, 0, 0, 0);
            color: $error;

            &:hover {
                background: rgba(0, 0, 0, 0.2);
            }
        }

        &.-grey-lighten {
            background: $panel-lighten-3;

            &:hover {
                background: $panel-lighten-1;
            }
        }

        &.-grey-darken {
            background: $panel-lighten-2;

            &:hover {
                background: $panel-lighten-1;
            }
        }
    }
    """

    variant: reactive[CliveButtonVariant]  # type: ignore[assignment]

    def __init__(
        self,
        label: TextType | None = None,
        variant: CliveButtonVariant = "primary",
        *,
        id_: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        ellipsis_: bool = False,
    ) -> None:
        self._ellipsis = ellipsis_
        super().__init__(
            label=self._create_label(label) if label is not None else None,
            variant=variant,  # type: ignore[arg-type]
            id=id_,
            classes=classes,
            disabled=disabled,
        )

    def on_focus(self) -> None:
        self.bind(Binding("enter", "press", str(self.label)))

    def update(self, new_label: TextType) -> None:
        self.label = self._create_label(new_label)
        self.refresh(layout=True)

    def validate_variant(self, variant: str) -> str:
        """No need for runtime validation, as invalid variant will be detected by mypy."""
        return variant

    def _create_label(self, label: TextType) -> TextType:
        return Text(str(label), no_wrap=True, overflow="ellipsis") if self._ellipsis else label
