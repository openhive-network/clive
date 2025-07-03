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


class GovernanceCheckboxLabel(Label):
    """Label introduced to be used with GovernanceCheckbox and easy query inside the GovernanceCheckbox."""


class GovernanceCheckbox(CliveWidget, can_focus=False):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    class Changed(Message):
        """Message send when checkbox in WitnessCheckbox changed."""

    class Clicked(Message):
        """Message send when WitnessCheckbox is clicked."""

    def __init__(self, *, is_voted: bool = False, initial_state: bool = False, disabled: bool = False) -> None:
        super().__init__(disabled=disabled)
        self._is_voted = is_voted
        self._checkbox = CheckBoxWithoutFocus(value=initial_state)
        self._initial_state = initial_state

    @property
    def value(self) -> bool:
        return self._checkbox.value

    def compose(self) -> ComposeResult:
        yield self._checkbox

        if self._initial_state:
            yield GovernanceCheckboxLabel("Vote" if not self._is_voted else "Unvote").add_class(
                "-voted" if self._is_voted else "-unvoted"
            )
        else:
            yield GovernanceCheckboxLabel("Vote" if not self._is_voted else "Unvote")

    def toggle(self) -> None:
        checkbox_label = self.query_exactly_one(GovernanceCheckboxLabel)

        if self._checkbox.value:
            self._checkbox.value = False
            checkbox_label.remove_class("-voted" if not self._is_voted else "-unvoted")
            return

        self._checkbox.value = True
        checkbox_label.add_class("-voted" if not self._is_voted else "-unvoted")

    @on(Checkbox.Changed)
    def checkbox_state_changed(self) -> None:
        self.post_message(self.Changed())

    @on(Click)
    def clicked(self) -> None:
        if not self.disabled:
            self.toggle()
            self.post_message(self.Clicked())
