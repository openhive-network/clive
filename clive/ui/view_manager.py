from __future__ import annotations

from typing import TYPE_CHECKING, Any, NoReturn

from prompt_toolkit.layout import Float, FloatContainer, to_container
from prompt_toolkit.widgets import Label

from clive.exceptions import ViewException
from clive.ui.focus import set_focus
from clive.ui.form_view import FormView
from clive.ui.menus.full.menu_full import MenuFull
from clive.ui.menus.menu import Menu
from clive.ui.menus.menu_empty import MenuEmpty
from clive.ui.rebuildable import Rebuildable
from clive.ui.view import View
from clive.ui.views.login import Login
from clive.ui.views.registration import Registration

if TYPE_CHECKING:
    from prompt_toolkit.layout import AnyContainer

    from clive.ui.base_float import BaseFloat


class ViewManager(Rebuildable):
    """
    A root that contains all other components.
    It doesn't define any layout, it just uses the one present in the currently set (active) view.
    Should be created only once.
    """

    def __init__(self) -> None:
        self.__active_view: View | FormView | None = None
        self.__float: BaseFloat | None = None

        self.__default_container = Label(text="No view selected... Loading...")
        self.__root_container = FloatContainer(self.__default_container, floats=[])
        self.__menu = MenuEmpty(self.__default_container)

    @property
    def active_container(self) -> AnyContainer:
        return self.__root_container

    @property
    def menu(self) -> Menu[Any]:
        return self.__menu

    @property
    def active_view(self) -> View | FormView:
        if self.__active_view is None:
            raise ViewException("No view was selected.")

        return self.__active_view

    @active_view.setter
    def active_view(self, value: View | FormView) -> None:
        self.__assert_if_proper_settable_type(value)
        self.__set_menu(value)

        self.__active_view = value
        self._rebuild()

    @property
    def float(self) -> BaseFloat | None:
        return self.__float

    @float.setter
    def float(self, value: BaseFloat | None) -> None:
        self.__float = value
        self.__root_container.floats = [Float(self.__float.container)] if self.__float is not None else []
        self._rebuild()

    def _rebuild(self) -> None:
        self.__menu.body = self.active_view.container
        self.__root_container.content = to_container(self.__menu.container)
        set_focus(self.__menu.body)

    @staticmethod
    def __assert_if_proper_settable_type(value: Any) -> NoReturn | None:
        settable = (View, FormView)
        if not isinstance(value, settable):
            raise ViewException(f"Could not set view to `{value}`. It must be an instance of {list(settable)}.")
        return None

    def __set_menu(self, value: View | FormView) -> None:
        menus: dict[type, tuple[type, ...]] = {
            MenuEmpty: (
                Login,
                Registration,
            ),
            MenuFull: (object,),  # this one is the default menu
        }

        for menu, views in menus.items():
            if isinstance(value, views):
                self.__menu = menu(self.__default_container)
                break


view_manager = ViewManager()
