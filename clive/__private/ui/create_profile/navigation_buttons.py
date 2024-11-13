from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import Static

from clive.__private.core.constants.tui.bindings import NEXT_SCREEN_BINDING_KEY, PREVIOUS_SCREEN_BINDING_KEY
from clive.__private.ui.widgets.buttons import CliveButton, OneLineButton

if TYPE_CHECKING:
    from typing import Final

    from textual.app import ComposeResult

FINISH_CREATE_PROFILE_BUTTON_LABEL: Final[str] = f"Finish! ({NEXT_SCREEN_BINDING_KEY})"


class NextScreenButton(CliveButton):
    """Button to go to the next create_profile screen."""

    DEFAULT_NEXT_BUTTON_LABEL: Final[str] = f"Next ({NEXT_SCREEN_BINDING_KEY}) →"

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
    """Button to go to the previous create_profile screen."""

    DEFAULT_PREVIOUS_BUTTON_LABEL: Final[str] = f"← Previous ({PREVIOUS_SCREEN_BINDING_KEY})"

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
    DEFAULT_CSS = """
    NavigationButtons {
        height: auto;

        CliveButton {
            margin: 0 1 0 1;
        }

        PreviousScreenButton {
            margin-top: 1;
            width: 2fr;
        }

        NextScreenButton {
            width: 2fr;
        }

        PlaceTaker {
            width: 4fr;
        }
    }
    """

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

    def compose(self) -> ComposeResult:
        yield PreviousScreenButton(self._previous_button_label)
        yield PlaceTaker()
        yield NextScreenButton(self._next_button_label)

    def set_finish_button(self) -> None:
        self.query_exactly_one(NextScreenButton).label = FINISH_CREATE_PROFILE_BUTTON_LABEL

    def set_next_screen_button(self) -> None:
        self.query_exactly_one(NextScreenButton).label = NextScreenButton.DEFAULT_NEXT_BUTTON_LABEL
