from __future__ import annotations

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import Button, Label

from clive.ui.component import Component
from clive.ui.components.buttons_menu import ButtonsMenu
from clive.ui.views.button_based import ButtonsBased


class MockMainPane(Component["MockButtonsBasedConcrete"]):
    def mock_main_exclusive(self) -> None:
        print("mock_main_exclusive")

    def _create_container(self) -> Label:
        return Label(text="Main")


class MockButtons(ButtonsMenu["MockButtonsBasedConcrete"]):
    def mock_buttons_exclusive(self) -> None:
        print("mock_buttons_exclusive")

    def _create_buttons(self) -> list[Button]:
        return [
            Button(text="Button 1"),
        ]

    def _get_key_bindings(self) -> KeyBindings:
        return KeyBindings()


class MockButtonsBasedConcrete(ButtonsBased[MockMainPane, MockButtons]):
    def __init__(self) -> None:
        super().__init__(MockMainPane(self), MockButtons(self))


def test_button_based_types() -> None:
    m = MockButtonsBasedConcrete()
    m.main_panel.mock_main_exclusive()  # should give no warning about missing attribute
    m.buttons.mock_buttons_exclusive()  # should give no warning about missing attribute
