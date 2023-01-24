from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.layout import VSplit, to_container
from prompt_toolkit.widgets import Label

from clive.exceptions import ViewException
from clive.ui.form_view import FormView
from clive.ui.menu import Menu
from clive.ui.rebuildable import Rebuildable
from clive.ui.view import View

if TYPE_CHECKING:
    from prompt_toolkit.layout import AnyContainer


class ViewManager(Rebuildable):
    """
    A root that contains all other components.
    It doesn't define any layout, it just uses the one present in the currently set (active) view.
    Should be created only once.
    """

    def __init__(self) -> None:
        self.__active_view: View | None = None
        self.__default_container = Label(text="No view selected... Loading...")
        self.__root_container = VSplit([self.__default_container])
        self.__menu = Menu(self.__default_container)

    @property
    def active_container(self) -> AnyContainer:
        return self.__root_container

    @property
    def menu(self) -> Menu:
        return self.__menu

    @property
    def active_view(self) -> View:
        if self.__active_view is None:
            raise ViewException("No view was selected.")

        return self.__active_view

    @active_view.setter
    def active_view(self, value: View) -> None:
        settable = (View, FormView)
        if not isinstance(value, settable):
            raise ViewException(f"Could not set view to `{value}`. It must be an instance of {list(settable)}.")

        self.__active_view = value
        self._rebuild()

    def _rebuild(self) -> None:
        self.__menu.body = self.active_view.container
        self.__root_container.children = [to_container(self.__menu.container)]


view_manager = ViewManager()
