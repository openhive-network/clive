from __future__ import annotations

from prompt_toolkit.layout import AnyContainer
from prompt_toolkit.widgets import MenuItem

from clive.ui.menus.menu import Menu
from clive.ui.menus.restricted.menu_restricted_handlers import MenuRestrictedHandlers


class MenuRestricted(Menu[MenuRestrictedHandlers]):
    def __init__(self, body: AnyContainer) -> None:
        super().__init__(body, MenuRestrictedHandlers(self))

    def _create_menu(self) -> list[MenuItem]:
        return [
            MenuItem(
                "Wallet",
                children=[
                    MenuItem("Dashboard", handler=self._handlers.dashboard),
                    MenuItem("Activate", handler=self._handlers.activate),
                    MenuItem("Exit", handler=self._handlers.exit),
                ],
            ),
            MenuItem(
                "Options",
                children=[
                    MenuItem("Set Node Address", handler=self._handlers.options_set_node_address),
                    MenuItem("Set Theme", handler=self._handlers.options_set_theme),
                ],
            ),
            MenuItem(
                "Help",
                children=[
                    MenuItem("Help", handler=self._handlers.help),
                    MenuItem("About", handler=self._handlers.about),
                    MenuItem("Contribute", handler=self._handlers.contribute),
                ],
            ),
        ]
