from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.reactive import var
from textual.widgets import Static

from clive.__private.core.constants.tui.bindings import NEXT_SCREEN_BINDING_KEY, PREVIOUS_SCREEN_BINDING_KEY
from clive.__private.ui.widgets.buttons import CliveButton, OneLineButton

if TYPE_CHECKING:
    from typing import Final

    from textual.app import ComposeResult


class NextScreenButton(CliveButton):
    """Button for going to next screen in forms (also used as finish button)."""

    DEFAULT_NEXT_BUTTON_LABEL: Final[str] = f"Next ({NEXT_SCREEN_BINDING_KEY}) →"
    FINISH_BUTTON_LABEL: Final[str] = f"Finish! ({NEXT_SCREEN_BINDING_KEY})"

    is_finish = var(default=False)

    class Pressed(CliveButton.Pressed):
        """Message sent when the NextScreenButton is pressed."""

    def __init__(
        self,
        *,
        is_finish: bool = False,
        id_: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            label=self._determine_label(is_finish=is_finish),
            variant="success",
            id_=id_,
            classes=classes,
            disabled=disabled,
        )
        self.set_reactive(self.__class__.is_finish, is_finish)

    def _watch_is_finish(self, value: bool) -> None:  # noqa: FBT001
        self.label = self._determine_label(is_finish=value)

    def _determine_label(self, *, is_finish: bool) -> str:
        return self.FINISH_BUTTON_LABEL if is_finish else self.DEFAULT_NEXT_BUTTON_LABEL


class PreviousScreenButton(OneLineButton):
    """Button for going to previous screen in forms."""

    DEFAULT_PREVIOUS_BUTTON_LABEL: Final[str] = f"← Previous ({PREVIOUS_SCREEN_BINDING_KEY})"

    class Pressed(OneLineButton.Pressed):
        """Message sent when the PreviousScreenButton is pressed."""

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

    is_finish = var(default=False)

    def __init__(
        self,
        id_: str | None = None,
        classes: str | None = None,
        *,
        is_finish: bool = False,
    ) -> None:
        super().__init__(id=id_, classes=classes)
        self.set_reactive(self.__class__.is_finish, is_finish)

    def compose(self) -> ComposeResult:
        yield PreviousScreenButton()
        yield PlaceTaker()
        yield NextScreenButton(is_finish=self.is_finish)

    def _watch_is_finish(self, value: bool) -> None:  # noqa: FBT001
        self.query_exactly_one(NextScreenButton).is_finish = value
