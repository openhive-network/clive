from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.layout import DynamicContainer
from prompt_toolkit.widgets import Label

from clive.exceptions import ViewException
from clive.ui.view import View

if TYPE_CHECKING:
    from prompt_toolkit.layout import AnyContainer


class ViewManager:
    """
    A root that contains all other components.
    It doesn't define any layout, it just uses the one present in the currently set (active) view.
    Should be created only once.
    """

    def __init__(self) -> None:
        self.__active_view: View | None = None
        self.__default_container = Label(text="No view selected... Loading...")
        self.__root_container = DynamicContainer(lambda: self.__create_container())

    def __create_container(self) -> AnyContainer:
        return self.__active_view.container if self.__active_view else self.__default_container

    @property
    def active_container(self) -> AnyContainer:
        return self.__root_container

    @property
    def active_view(self) -> View | None:
        return self.__active_view

    @active_view.setter
    def active_view(self, value: View) -> None:
        if not isinstance(value, View):
            raise ViewException(f"Could not set view to `{value}`. It must be an instance of `{View}`.")

        self.__active_view = value


view_manager = ViewManager()
