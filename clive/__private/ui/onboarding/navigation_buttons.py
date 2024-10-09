from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import Static

from clive.__private.ui.widgets.buttons import CliveButton, OneLineButton

if TYPE_CHECKING:
    from typing import Final

    from textual.app import ComposeResult

FINISH_ONBOARDING_BUTTON_LABEL: Final[str] = "Finish!"


class NextScreenButton(CliveButton):
    """Button to go to the next onboarding screen."""

    DEFAULT_NEXT_BUTTON_LABEL: Final[str] = "Next →"

    class Pressed(CliveButton.Pressed):
        """Message sent when the next screen button is pressed."""

    def __init__(
        self,
        label: str = DEFAULT_NEXT_BUTTON_LABEL,
        *,
        id_: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(label=label, variant="success", id_=id_, classes=classes, disabled=disabled)


class PreviousScreenButton(OneLineButton):
    """Button to go to the previous onboarding screen."""

    DEFAULT_PREVIOUS_BUTTON_LABEL: Final[str] = "← Previous"

    class Pressed(OneLineButton.Pressed):
        """Message sent when the previous screen button is pressed."""

    def __init__(
        self,
        label: str = DEFAULT_PREVIOUS_BUTTON_LABEL,
        *,
        id_: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(label=label, variant="transparent", id_=id_, classes=classes, disabled=disabled)


class PlaceTaker(Static):
    pass


class NavigationButtons(Horizontal):
    def __init__(
        self,
        next_button_label: str = NextScreenButton.DEFAULT_NEXT_BUTTON_LABEL,
        previous_button_label: str = PreviousScreenButton.DEFAULT_PREVIOUS_BUTTON_LABEL,
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id_, classes=classes)
        self._next_button_label = next_button_label
        self._previous_button_label = previous_button_label

    DEFAULT_CSS = """
    NavigationButtons {
        height: auto;

        CliveButton {
            margin: 0 1 0 1;
        }

        PreviousScreenButton {
            margin-top: 1;
            width: 1fr;
        }

        NextScreenButton {
            width: 2fr;
        }

        PlaceTaker {
            width: 4fr;
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield PreviousScreenButton(self._previous_button_label)
        yield PlaceTaker()
        yield NextScreenButton(self._next_button_label)
