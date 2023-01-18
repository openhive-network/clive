from __future__ import annotations

from abc import ABC
from typing import Sequence

from loguru import logger
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent, merge_key_bindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import AnyContainer, HSplit, VSplit
from prompt_toolkit.widgets import Box, Button, Frame, Label, TextArea

from clive.ui.component import Component
from clive.ui.components.buttons_menu import ButtonsMenu
from clive.ui.focus import set_focus
from clive.ui.view import DynamicView
from clive.ui.view_switcher import switch_view


class RegistrationForm(Component):
    def __init__(self):
        self.__profile_name_input = TextArea(style="class:tertiary", focus_on_click=True)
        self.__password_input = TextArea(style="class:tertiary", password=True, focus_on_click=True)
        self.__password_repeat_input = TextArea(style="class:tertiary", password=True, focus_on_click=True)

        super().__init__()

    def _create_container(self) -> AnyContainer:
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


class RegistrationButtons(ButtonsMenu):
    def __init__(self) -> None:
        super().__init__()

    def _create_buttons(self) -> Sequence[Button]:
        return [Button("F1 Help", handler=self.__f1_action), Button("F2 Create Profile", handler=self.__f2_action)]

    def _get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()
        kb.add(Keys.F1)(self.__f1_action)
        kb.add(Keys.F2)(self.__f2_action)
        return kb

    def __f1_action(self, event: KeyPressEvent | None = None) -> None:
        print(self.context.main_pane.profile_name)

    def __f2_action(self, event: KeyPressEvent | None = None) -> None:
        # print(self.context.main_pane.profile_name)
        switch_view('dashboard')


class ButtonsBased(DynamicView, ABC):
    def __init__(self, main_pane: Component, buttons: ButtonsMenu | None = None) -> None:
        self._buttons = buttons
        self._main_pane = main_pane
        super().__init__()

    def _create_container(self) -> HSplit:
        return HSplit(
            [
                Frame(self._main_pane.container),
                Frame(self.__get_buttons_container(), style="class:primary"),
            ],
            style="class:primary",
            key_bindings=merge_key_bindings(self._key_bindings),
        )

    def __get_buttons_container(self) -> AnyContainer:
        return self._buttons.container if self._buttons else Label("No buttons")

    @property
    def key_bindings(self) -> list[KeyBindings]:
        return self._key_bindings


class Registration(ButtonsBased):
    def __init__(self):
        main_pane = RegistrationForm()
        buttons = RegistrationButtons()
        super().__init__(main_pane, buttons)
        self._buttons.context = self

    @property
    def main_pane(self):
        return self._main_pane
