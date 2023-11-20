from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.events import Click
from textual.message import Message
from textual.widgets import Checkbox, Label

from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult


class CheckBoxWithoutFocus(Checkbox):
    can_focus = False

    def toggle(self) -> None:  # type: ignore[override]
        """Changing the value of a checkbox is managed by WitnessCheckbox."""


class WitnessCheckBoxChanged(Message):
    """
    Message send when checkbox in WitnessCheckbox changed.

    The widget that is used cannot detect Checkbox.Changed, so it is required to use this message in the  on decorator.
    """


class WitnessCheckbox(CliveWidget, can_focus=False):
    DEFAULT_CSS = """
    Label {
        text-align: center;
        width: 1fr;
    }
    """

    def __init__(
        self, related_witness: CliveWidget, classes: str, is_voted: bool = False, initial_state: bool = False
    ) -> None:
        super().__init__(classes=classes)
        self.__is_voted = is_voted
        self.__checkbox = CheckBoxWithoutFocus(value=initial_state)
        self.__related_witness = related_witness

        if initial_state:
            self.add_class("-voted" if not self.__is_voted else "-unvoted")

    def compose(self) -> ComposeResult:
        yield self.__checkbox
        if not self.__is_voted:
            yield Label("Vote")
        else:
            yield Label("Unvote")

    def on_click(self) -> None:
        self.press()

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
        self.post_message(WitnessCheckBoxChanged())

    @on(Click)
    def set_focus_to_related_witness(self) -> None:
        self.app.set_focus(self.__related_witness)
