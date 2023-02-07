from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, TypeVar

from clive.abstract_class import AbstractClass
from clive.ui.parented import Parented

if TYPE_CHECKING:
    from clive.ui.menus.menu import Menu

T = TypeVar("T", bound="Menu[Any]")


class MenuHandlers(Parented[T], AbstractClass):
    def __init__(self, parent: T) -> None:
        super().__init__(parent)

    def _switch_view(self, target_view: type, **kwargs: Any) -> Callable[[], None]:
        def default_switch_view_impl() -> None:
            from clive.ui.view_switcher import switch_view

            if self.__ask_about_loosing_changes():
                switch_view(target_view(**kwargs))

        return default_switch_view_impl

    def __ask_about_loosing_changes(self) -> bool:
        """
        This method should check is there some unsaved progress and
        if so it should ask user about continuation

        TODO: Implement this function

        Returns:
            bool: True if switching can be continued, False otherwise
        """
        return True
