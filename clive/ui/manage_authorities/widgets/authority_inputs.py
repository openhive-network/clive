from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.containers import Horizontal
from textual.widgets import Input, Static, Switch

if TYPE_CHECKING:
    from rich.highlighter import Highlighter
    from textual.app import ComposeResult


class AuthorityInput(Input):
    def __init__(
        self,
        value: str | None = None,
        highlighter: Highlighter | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(value, self._placeholder(), highlighter, False, None, id, classes, False)

    def _placeholder(self) -> str:
        return ""

    def _condition(self, value: bool) -> bool:
        return value

    def on_switch_changed(self, ev: Switch.Changed) -> None:
        hidden_class: Final[str] = "hidden"
        if ev.input.id == "input_type" and self._condition(ev.value):
            self.add_class(hidden_class)
            self.remove_class(hidden_class)


class AuthorityInputSwitch(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("Input private key")
        yield Switch(False, id="input_type")
        yield Static("Input path to private key")


class RawAuthorityDefinition(AuthorityInput):
    def _placeholder(self) -> str:
        return "authority definition"


class AuthorityDefinitionFromFile(AuthorityInput):
    def _placeholder(self) -> str:
        return "path to authority definition"

    def _condition(self, value: bool) -> bool:
        return not value
