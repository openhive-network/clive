from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.reactive import var
from textual.widgets import Static

from clive.__private.ui.widgets.buttons import CliveButton, OneLineButton

if TYPE_CHECKING:
    from textual.app import ComposeResult


class NextScreenButton(CliveButton):
    """
    Button for going to next screen in forms (also used as finish button).

    Attributes:
        is_finish: Whether this button is used to finish the form.

    Args:
        is_finish: Whether this button is used to finish the form.
        id_: The ID of the button in the DOM.
        classes: The CSS classes for the button.
        disabled: Whether the button should be disabled initially.
    """

    is_finish = var(default=False, init=False)

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
        return "Finish!" if is_finish else "Next →"


class PreviousScreenButton(OneLineButton):
    """
    Button for going to previous screen in forms.

    Args:
        label: Label for the button.
        id_: The ID of the button in the DOM.
        classes: The CSS classes for the button.
        disabled: Whether the button should be disabled initially.
    """

    class Pressed(OneLineButton.Pressed):
        """Message sent when the PreviousScreenButton is pressed."""

    def __init__(
        self,
        label: str | None = None,
        *,
        id_: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            label=self._get_init_label(label),
            variant="transparent",
            id_=id_,
            classes=classes,
            disabled=disabled,
        )

    def _get_init_label(self, label: str | None) -> str:
        return label if label is not None else "← Previous"


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

    is_finish = var(default=False, init=False)

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
