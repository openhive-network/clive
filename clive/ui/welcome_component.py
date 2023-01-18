from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import HorizontalAlign, HSplit, VSplit, WindowAlign
from prompt_toolkit.widgets import Button, Label

from clive.ui.view import View
from clive.ui.view_switcher import switch_view

if TYPE_CHECKING:
    from prompt_toolkit.key_binding import KeyPressEvent


class WelcomeComponent(View):
    """A component that is displayed when the user first starts the application."""

    def _create_container(self) -> HSplit:
        return HSplit(
            [
                Label(text="Welcome to CLIVE!", align=WindowAlign.CENTER),
                Label(text="Press the button below or any key to continue...", align=WindowAlign.CENTER),
                VSplit(
                    [
                        Button(text="Continue", handler=self.__continue),
                    ],
                    align=HorizontalAlign.CENTER,
                ),
            ],
            style="class:secondary",
            key_bindings=self.__get_key_bindings(),
        )

    @staticmethod
    def __continue(event: KeyPressEvent | None = None) -> None:
        switch_view("dashboard")

    def __get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()
        kb.add(Keys.Any)(self.__continue)

        return kb
