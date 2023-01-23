from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.layout import HSplit, VSplit
from prompt_toolkit.widgets import Box, Label, TextArea

from clive.ui.component import Component

if TYPE_CHECKING:
    from clive.ui.views.registration import Registration


class RegistrationForm(Component["Registration"]):
    def __init__(self, parent: Registration) -> None:
        self.__profile_name_input = TextArea(style="class:tertiary", focus_on_click=True)
        self.__password_input = TextArea(style="class:tertiary", password=True, focus_on_click=True)
        self.__password_repeat_input = TextArea(style="class:tertiary", password=True, focus_on_click=True)

        super().__init__(parent)

    def _create_container(self) -> Box:
        return Box(
            HSplit(
                [
                    Label("In order to use CLIVE you should create a profile and set the password to it."),
                    VSplit(
                        [
                            HSplit(
                                [
                                    Label("Profile name:"),
                                    Label("Password: "),
                                    Label("Repeat password: "),
                                ],
                            ),
                            HSplit(
                                [
                                    self.__profile_name_input,
                                    self.__password_input,
                                    self.__password_repeat_input,
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

    @property
    def password_repeat(self) -> str:
        return self.__password_repeat_input.text
