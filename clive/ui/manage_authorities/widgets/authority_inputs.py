from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import Input, Static, Switch

if TYPE_CHECKING:
    from rich.highlighter import Highlighter
    from textual.app import ComposeResult


class AuthorityInput(Input):
    pass


class RawAuthorityDefinition(AuthorityInput):
    def __init__(
        self,
        value: str,
        *,
        highlighter: Highlighter | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(value, "authority definition", highlighter, False, name, id, classes)


class AuthorityDefinitionFromFile(AuthorityInput):
    def __init__(
        self,
        *,
        highlighter: Highlighter | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(None, "path to authority definition", highlighter, False, name, id, classes)


class AuthorityInputSwitch(Horizontal):
    def __init__(
        self,
        right: AuthorityInput,
        left: AuthorityInput,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self.__right = right
        self.__left = left
        super().__init__(id=id, classes=classes)

    def compose(self) -> ComposeResult:
        yield Static("Input private key")
        yield Switch(False, id="input_type")
        yield Static("Input path to private key")

    def on_mount(self) -> None:
        def set_hidden(obj: AuthorityInput, value: bool) -> None:
            if value:
                obj.add_class("hidden")
            else:
                obj.remove_class("hidden")

        s = self.query_one(Switch)
        self.__right.watch(s, "value", lambda: set_hidden(self.__right, s.value), init=True)
        self.__left.watch(s, "value", lambda: set_hidden(self.__left, not s.value), init=True)
