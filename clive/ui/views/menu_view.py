from abc import ABC, abstractmethod
from typing import List

from prompt_toolkit.layout import AnyContainer, to_container
from prompt_toolkit.widgets import MenuContainer, MenuItem
from clive.ui.component import safe_edit

from clive.ui.view import ConfigurableView
from clive.ui.view_manager import ViewManager


class MenuView(ConfigurableView, ABC):
    def __init__(self, parent: ViewManager):
        self.container: MenuContainer
        super().__init__(parent)

        self.__body: AnyContainer

    @abstractmethod
    def _menu_structure(self) -> List[MenuItem]: ...

    @property
    def body(self) -> AnyContainer:
        return self.__body

    @body.setter
    @safe_edit
    def body(self, value: AnyContainer) -> None:
        self.__body = value

    # def disable_all(self) -> None:
    #     self.container.menu_items = self.__set_all_to(self.container.menu_items, True)

    # def enable_all(self) -> None:
    #     self.container.menu_items = self.__set_all_to(self.container.menu_items, False)

    # def __set_all_to(self, menu_items: List[MenuItem], value: bool) -> List[MenuItem]:
    #     for mi in menu_items:
    #         mi.disabled = value
    #         if mi.children is not None and len(mi.children) > 0:
    #             mi.children = self.__set_all_to(mi.children, value)
    #     return menu_items

    def _create_container(self) -> MenuContainer:
        return MenuContainer(body=to_container(self.body), menu_items=self._menu_structure())
