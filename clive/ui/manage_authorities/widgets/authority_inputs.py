from __future__ import annotations

from typing import TYPE_CHECKING, Final, cast

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
        self.__hidden_class: Final[str] = "hidden"
        self.__right = right
        self.__left = left
        self.__left.add_class(self.__hidden_class)
        super().__init__(id=id, classes=classes)

    def compose(self) -> ComposeResult:
        yield Static("Input private key")
        yield Switch(False, id="input_type")
        yield Static("Input path to private key")

    def __swap_visibility(self) -> None:
        for auth_in in [self.__right, self.__left]:
            if auth_in.has_class(self.__hidden_class):
                auth_in.remove_class(self.__hidden_class)
            else:
                auth_in.add_class(self.__hidden_class)

    def on_switch_changed(self, event: Switch.Changed) -> None:
        sender = cast(Switch, event.sender)
        if sender.id == "input_type":
            self.__swap_visibility()
