from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from textual import on
from textual.events import Click
from textual.message import Message
from textual.widgets import Checkbox, Label

from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.screens.operations.governance_operations.common_governance.governance_actions import (
    GovernanceActionStatus,
)

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from typing_extensions import Self


class CheckBoxWithoutFocus(Checkbox):
    can_focus = False

    def toggle(self) -> Self:
        """Do nothing. Changing the value of a checkbox is managed by WitnessCheckbox."""
        return self


class GovernanceCheckbox(CliveWidget, can_focus=False):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    @dataclass
    class Changed(Message):
        """Message send when checkbox in WitnessCheckbox changed."""

        status: GovernanceActionStatus
        add: bool = False

    class Clicked(Message):
        """Message send when WitnessCheckbox is clicked."""

    def __init__(self, *, is_voted: bool = False, initial_state: bool = False, pending: bool = False) -> None:
        super().__init__()
        self._pending = pending
        self.__is_voted = is_voted
        self.__checkbox = CheckBoxWithoutFocus(value=initial_state)

    def compose(self) -> ComposeResult:
        yield self.__checkbox
        yield Label("Vote" if not self.__is_voted else "Unvote")

    def toggle(self) -> None:
        if self.__checkbox.value:
            self.__checkbox.value = False
            return

        self.__checkbox.value = True

    @property
    def value(self) -> bool:
        return self.__checkbox.value

    @on(Checkbox.Changed)
    def checkbox_state_changed(self) -> None:
        vote_status = "unvote" if self.__is_voted else "vote"

        if self._pending:
            self.post_message(self.Changed(cast(GovernanceActionStatus, f"pending_{vote_status}")))
            self._pending = False
            return

        self.post_message(self.Changed(cast(GovernanceActionStatus, vote_status), add=self.__checkbox.value))

    @on(Click)
    def clicked(self) -> None:
        self.toggle()
        self.post_message(self.Clicked())
