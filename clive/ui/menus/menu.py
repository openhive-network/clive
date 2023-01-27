from __future__ import annotations

import typing
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from prompt_toolkit.widgets import MenuContainer

from clive.ui.containerable import Containerable
from clive.ui.rebuildable import Rebuildable

if TYPE_CHECKING:
    from typing import Any  # noqa: F401

    from prompt_toolkit.layout import AnyContainer
    from prompt_toolkit.widgets import MenuItem

    from clive.ui.menus.menu_handlers import MenuHandlers  # noqa: F401


T = TypeVar("T", bound="MenuHandlers[Any]")


class Menu(Containerable, Rebuildable, Generic[T], ABC):
    def __init__(self, body: AnyContainer, handlers: T) -> None:
        self.__body = body
        self._handlers = handlers
        super().__init__()

    @property
    def body(self) -> AnyContainer:
        return self.__body

    @body.setter
    def body(self, value: AnyContainer) -> None:
        self.__body = value
        self._rebuild()

    @abstractmethod
    def _create_menu(self) -> list[MenuItem]:
        """Create a list of MenuItems which will be later used in MenuContainer."""

    def _rebuild(self) -> None:
        self._container = self._create_container()

    def _create_container(self) -> MenuContainer:
        return MenuContainer(
            body=self.body,
            menu_items=self._create_menu(),
        )

    @property
    def container(self) -> MenuContainer:
        return typing.cast(MenuContainer, super().container)
