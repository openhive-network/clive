from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.events import Click
from textual.message import Message
from textual.widgets import Checkbox, Label

from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.get_css import get_css_from_relative_path

if TYPE_CHECKING:
    from typing import Self

    from textual.app import ComposeResult


class CheckBoxWithoutFocus(Checkbox):
    can_focus = False

    def toggle(self) -> Self:
        """Do nothing. Changing the value of a checkbox is managed by WitnessCheckbox."""
        return self


class GovernanceCheckbox(CliveWidget, can_focus=False):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    class Changed(Message):
        """Message send when checkbox in WitnessCheckbox changed."""

    class Clicked(Message):
        """Message send when WitnessCheckbox is clicked."""

    def __init__(self, *, is_voted: bool = False, initial_state: bool = False, disabled: bool = False) -> None:
        super().__init__(disabled=disabled)
        self.__is_voted = is_voted
        self.__checkbox = CheckBoxWithoutFocus(value=initial_state)

        if initial_state:
            self.add_class("-voted" if not self.__is_voted else "-unvoted")

    def compose(self) -> ComposeResult:
        yield self.__checkbox
        yield Label("Vote" if not self.__is_voted else "Unvote")

    def toggle(self) -> None:
        if self.disabled:
            return

        if self.__checkbox.value:
            self.__checkbox.value = False
            self.remove_class("-voted" if not self.__is_voted else "-unvoted")
            return

        self.__checkbox.value = True
        self.add_class("-voted" if not self.__is_voted else "-unvoted")

    @property
    def value(self) -> bool:
        return self.__checkbox.value

    @on(Checkbox.Changed)
    def checkbox_state_changed(self) -> None:
        self.post_message(self.Changed())

    @on(Click)
    def clicked(self) -> None:
        if not self.disabled:
            self.toggle()
            self.post_message(self.Clicked())
