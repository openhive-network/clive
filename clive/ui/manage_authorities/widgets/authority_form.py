from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

from textual.containers import Container, Vertical
from textual.widgets import Input

from clive.ui.manage_authorities.widgets.authority_inputs import (
    AuthorityDefinitionFromFile,
    AuthorityInputSwitch,
    RawAuthorityDefinition,
)
from clive.ui.manage_authorities.widgets.authority_submit_buttons import AuthoritySubmitButtons
from clive.ui.widgets.big_tittle import BigTittle

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.storage.mock_database import PrivateKey


class AuthorityForm(Container):
    def __init__(self, authority: PrivateKey, callback: Callable[[], None], title: str) -> None:
        self.__authority = authority
        self.__callback = callback
        self.__title = title
        super().__init__()

    def compose(self) -> ComposeResult:
        raw_input = RawAuthorityDefinition(self.__authority.key)
        file_input = AuthorityDefinitionFromFile()
        name = Input(self.__authority.key_name, "authority name")

        def on_close() -> None:
            self.app.pop_screen()

        def on_save() -> None:
            self.__authority.key_name = name.value
            if not raw_input.has_class("hidden"):
                self.__authority.key = raw_input.value
            else:
                path = Path(file_input.value)
                with path.open("rt") as file:
                    self.__authority.key = file.readline().strip("\n")
            self.__callback()
            on_close()

        with Vertical():
            yield BigTittle(self.__title)
            yield name
            yield AuthorityInputSwitch(raw_input, file_input)
            yield Container(raw_input, file_input)
            yield AuthoritySubmitButtons(on_save, on_close)
