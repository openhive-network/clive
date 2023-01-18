from __future__ import annotations

from abc import ABC
from typing import Sequence

from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import AnyContainer, HSplit, VSplit
from prompt_toolkit.widgets import Box, Button, Frame, Label, TextArea

from clive.ui.component import Component
from clive.ui.components.buttons_menu import ButtonsMenu
from clive.ui.view import DynamicView


class RegistrationForm(Component):
    def __init__(self):
        self.__profile_name_input = TextArea(style="class:primary")
        self.__password_input = TextArea(style="class:primary", password=True)
        self.__password_repeat_input = TextArea(style="class:primary", password=True)

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
                                ]
                            ),
                            HSplit(
                                [
                                    self.__profile_name_input,
                                    self.__password_input,
                                    self.__password_repeat_input,
                                ]
                            ),
                        ]
                    ),
                ]
            )
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
    def __init__(self, parent: Registration) -> None:
        self.__parent = parent
        super().__init__()

        self.__parent.key_bindings.append(self._key_bindings)

    def _create_buttons(self) -> Sequence[Button]:
        return [Button("F1 Help"), Button("F2 Create Profile", handler=self.__f2_action)]

    def _get_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()
        kb.add(Keys.F2)(self.__f2_action)
        return kb

    def __f2_action(self) -> None:
        print(self.__parent.main_pane.profile_name)


class ButtonsBased(DynamicView, ABC):
    def __init__(self, main_pane: Component, buttons: ButtonsMenu):
        self._key_bindings: list[KeyBindings] = []
        self.__main_pane = main_pane
        self.__buttons = buttons
        super().__init__()

    def _create_container(self) -> HSplit:
        return HSplit(
            [
                self.__main_pane.container,
                Frame(self.__buttons.container, style="class:primary"),
            ],
            key_bindings=merge_key_bindings(self._key_bindings),
        )

    @property
    def key_bindings(self) -> list[KeyBindings]:
        return self._key_bindings


class Registration(ButtonsBased):
    def __init__(self):
        self._key_bindings: list[KeyBindings] = []
        self.__main_pane = RegistrationForm()
        self.__buttons = RegistrationButtons(self)
        super().__init__(self.__main_pane, self.__buttons)
        print(self._key_bindings)

    @property
    def main_pane(self) -> RegistrationForm:
        return self.__main_pane
