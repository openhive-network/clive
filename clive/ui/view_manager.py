from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, NoReturn

from loguru import logger
from prompt_toolkit.layout import FloatContainer, to_container
from prompt_toolkit.widgets import Label

from clive.app_status import app_status
from clive.exceptions import ViewException
from clive.ui.floats import Floats
from clive.ui.focus import set_focus
from clive.ui.form_view import FormView
from clive.ui.menus.full.menu_full import MenuFull
from clive.ui.menus.menu import Menu
from clive.ui.menus.menu_empty import MenuEmpty
from clive.ui.menus.restricted.menu_restricted import MenuRestricted
from clive.ui.rebuildable import Rebuildable
from clive.ui.view import View
from clive.ui.views.login import Login
from clive.ui.views.registration import Registration

if TYPE_CHECKING:
    from prompt_toolkit.layout import AnyContainer


class ViewManager(Rebuildable):
    """
    A root that contains all other components.
    It doesn't define any layout, it just uses the one present in the currently set (active) view.
    Should be created only once.
    """

    def __init__(self) -> None:
        self.__active_view: View | FormView | None = None

        self.__default_container = Label(text="No view selected... Loading...")
        self.__floats = Floats(self)

        self.__root_container = FloatContainer(self.__default_container, floats=self.floats.content)
        self.__menu: Menu[Any] = MenuEmpty(self.__default_container)

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

        self.__active_view = value
        self._rebuild()

    @property
    def floats(self) -> Floats:
        return self.__floats

    def rebuild(self) -> None:
        self._rebuild()

    def _rebuild(self) -> None:
        logger.debug(f"rebuilding component: {self.__class__.__name__}")
        self.__set_menu(self.active_view)
        self.__menu.body = self.active_view.container
        self.__root_container.content = to_container(self.__menu.container)
        self.__root_container.floats = self.floats.content
        if not self.floats.float and not self.floats.error_float:
            set_focus(self.__menu.body)

    @staticmethod
    def __assert_if_proper_settable_type(value: Any) -> NoReturn | None:
        settable = (View, FormView)
        if not isinstance(value, settable):
            raise ViewException(f"Could not set view to `{value}`. It must be an instance of {list(settable)}.")
        return None

    def __set_menu(self, value: View | FormView) -> None:
        menus: dict[type, Callable[[], bool]] = {
            MenuEmpty: lambda: isinstance(value, (Login, Registration)),
            MenuRestricted: lambda: not app_status.active_mode,
            MenuFull: lambda: app_status.active_mode,
        }

        for menu, predicate in menus.items():
            if predicate():
                self.__menu = menu(self.__default_container)
                break


view_manager = ViewManager()
