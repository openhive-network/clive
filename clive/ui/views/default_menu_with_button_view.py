
from typing import List
from prompt_toolkit.layout import AnyContainer
from prompt_toolkit.widgets import Button
from clive.ui.menu_handlers import MenuHandlers
from prompt_toolkit.key_binding import KeyBindings

from clive.ui.view import ConfigurableView, ReadyView
from clive.ui.views.button_based import ButtonsBased
from clive.ui.views.dashboard import Dashboard
from clive.ui.views.default_menu_view import DefaultMenuView
from clive.ui.components.buttons_menu import ButtonsMenu

class MockButtons(ButtonsMenu[ButtonsBased]):
    def mock_buttons_exclusive(self) -> None:
        print("mock_buttons_exclusive")

    def _create_buttons(self) -> List[Button]:
        return [
            Button(text="Button 1"),
        ]

    def _get_key_bindings(self) -> KeyBindings:
        return KeyBindings()

class DefaultMenuWithButtonView(ReadyView):
    def _create_container(self) -> DefaultMenuView:
        with DefaultMenuView(parent=self._parent) as dmv:
            with ButtonsBased(parent=dmv) as bb:
                bb.main_panel = Dashboard(parent=bb)
                bb.buttons = MockButtons(parent=bb)

            dmv.body = bb.container
            dmv.handlers = MenuHandlers(parent=dmv)
        return dmv.container

