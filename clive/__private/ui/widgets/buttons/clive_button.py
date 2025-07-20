from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from rich.text import Text
from textual import on
from textual.widgets import Button
from textual.widgets._button import ButtonVariant

from clive.__private.ui.clive_widget import CliveWidget

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.reactive import reactive

    from clive.__private.ui.bindings.clive_binding import CliveBinding


CliveButtonVariant = Literal[
    "loading-variant",
    "success-on-transparent",
    "error-on-transparent",
    "transparent",
    "grey-darken",
    "grey-lighten",
    "darken-primary",
    ButtonVariant,
]


class CliveButton(Button, CliveWidget):
    """
    A regular Textual button which also displays "enter" action binding.

    Attributes:
        DEFAULT_CSS: Default CSS styles for the button.
        variant: The variant of the button.

    Args:
        label: The label of the button.
        variant: The variant of the button.
        binding: Optional binding to display next to the label.
        id_: Optional ID for the button.
        classes: Optional CSS classes for the button.
        disabled: Whether the button is disabled.
        ellipsis_: Whether to apply ellipsis to the label text.

    """

    class Pressed(Button.Pressed):
        """Event sent when a `CliveButton` is pressed."""

    DEFAULT_CSS = """
    CliveButton {
        &.-success {
            background: $success-darken-1;

            &:hover {
                background: $success-darken-3;
            }
        }

        &.-loading-variant {
            background: $panel-lighten-2;

            &:hover {
                background: $panel-lighten-1;
            }
        }

        &.-success-on-transparent {
            background: 0%;
            color: $success-darken-3;

            &:hover {
                background: black 20%;
            }
        }

        &.-error-on-transparent {
            background: 0%;
            color: $error;

            &:hover {
                background: black 20%;
            }
        }

         &.-transparent {
            background: 0%;

            &:hover {
                background: black 20%;
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

        &.-darken-primary {
            background: $primary-darken-1;

            &:hover {
                background: $primary-darken-3;
            }
        }
    }
    """

    variant: reactive[CliveButtonVariant]

    def __init__(
        self,
        label: TextType | None = None,
        variant: CliveButtonVariant = "primary",
        *,
        binding: CliveBinding | None = None,
        id_: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        ellipsis_: bool = False,
    ) -> None:
        self._ellipsis = ellipsis_
        super().__init__(
            label=self._create_label(label, binding) if label is not None else None,
            variant=variant,  # type: ignore[arg-type]
            id=id_,
            classes=classes,
            disabled=disabled,
        )

    def update(self, new_label: TextType, binding: CliveBinding | None = None) -> None:
        self.label = self._create_label(new_label, binding)
        self.refresh(layout=True)

    @on(Button.Pressed)
    def fix_for_textual_button_pressed_namespace(self, event: Button.Pressed) -> None:
        """
        Change Button.Pressed namespace to self.Pressed to allow for correct namespace handling.

        Related issues:
            - https://github.com/Textualize/textual/issues/4967
            - https://github.com/Textualize/textual/issues/1814

        Args:
            event: The Button.Pressed event that was triggered.
        """
        if type(event) is Button.Pressed:
            event.stop()
            self.post_message(self.Pressed(self))

    def validate_variant(self, variant: str) -> str:
        """
        No need for runtime validation, as invalid variant will be detected by mypy.

        Args:
            variant: The variant to validate.

        Returns:
            The validated variant.
        """
        return variant

    def _create_label(self, label: TextType, binding: CliveBinding | None = None) -> TextType:
        binding_button_display = binding.button_display if binding else None
        text = f"{label}" if not binding_button_display else f"{label} ({binding_button_display})"
        return Text(text, no_wrap=True, overflow="ellipsis") if self._ellipsis else text
