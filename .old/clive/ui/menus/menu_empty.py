from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.widgets import MenuItem

from clive.ui.menus.menu import Menu
from clive.ui.menus.menu_handlers import MenuHandlers

if TYPE_CHECKING:
    from prompt_toolkit.layout import AnyContainer


class MenuEmptyHandlers(MenuHandlers["MenuEmpty"]):
    def __init__(self, parent: MenuEmpty) -> None:
        super().__init__(parent)


class MenuEmpty(Menu[MenuEmptyHandlers]):
    """A special type of menu used when the menu should not be displayed."""

    def __init__(self, body: AnyContainer) -> None:
        super().__init__(body, MenuEmptyHandlers(self))

    def _create_menu(self) -> list[MenuItem]:
        return [MenuItem("")]
