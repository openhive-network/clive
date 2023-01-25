from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.layout import HSplit, VSplit
from prompt_toolkit.widgets import Box, Label, TextArea

from clive.ui.component import Component

if TYPE_CHECKING:
    from clive.ui.views.login import Login


class LoginForm(Component["Login"]):
    def __init__(self, parent: Login) -> None:
        self.__profile_name_input = TextArea(style="class:tertiary", focus_on_click=True)
        self.__password_input = TextArea(style="class:tertiary", password=True, focus_on_click=True)

        super().__init__(parent)

    def _create_container(self) -> Box:
        return Box(
            HSplit(
                [
                    Label("Please enter your credentials to log in and continue."),
                    VSplit(
                        [
                            HSplit(
                                [
                                    Label("Profile name:"),
                                    Label("Password: "),
                                ],
                            ),
                            HSplit(
                                [
                                    self.__profile_name_input,
                                    self.__password_input,
                                ],
                            ),
                        ],
                        style="#000000",
                    ),
                ],
                style="class:primary",
            ),
            style="class:secondary",
        )

    @property
    def profile_name(self) -> str:
        return self.__profile_name_input.text

    @property
    def password(self) -> str:
        return self.__password_input.text
