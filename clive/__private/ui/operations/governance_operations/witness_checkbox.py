from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.events import Click
from textual.message import Message
from textual.widgets import Checkbox, Label

from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult


class CheckBoxWithoutFocus(Checkbox):
    can_focus = False

    def toggle(self) -> None:  # type: ignore[override]
        """Changing the value of a checkbox is managed by WitnessCheckbox."""


class WitnessCheckbox(CliveWidget, can_focus=False):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    class Changed(Message):
        """Message send when checkbox in WitnessCheckbox changed."""

    class Clicked(Message):
        """Message send when WitnessCheckbox is clicked."""

    def __init__(self, is_voted: bool = False, initial_state: bool = False) -> None:
        super().__init__()
        self.__is_voted = is_voted
        self.__checkbox = CheckBoxWithoutFocus(value=initial_state)

        if initial_state:
            self.add_class("-voted" if not self.__is_voted else "-unvoted")

    def compose(self) -> ComposeResult:
        yield self.__checkbox
        if not self.__is_voted:
            yield Label("Vote")
        else:
            yield Label("Unvote")

    def press(self) -> None:
        if self.__checkbox.value:
            self.__checkbox.value = False
            self.remove_class("-voted" if not self.__is_voted else "-unvoted")
            return
        self.__checkbox.value = True
        self.add_class("-voted" if not self.__is_voted else "-unvoted")

    @property
    def checkbox_state(self) -> bool:
        return self.__checkbox.value

    @on(Checkbox.Changed)
    def checkbox_state_changed(self) -> None:
        self.post_message(self.Changed())

    @on(Click)
    def clicked(self) -> None:
        self.press()
        self.post_message(self.Clicked())
