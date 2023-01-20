from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

from prompt_toolkit.layout import to_container

from clive.exceptions import ViewException
from clive.ui.form_view import FormView
from clive.ui.rebuildable import Rebuildable
from clive.ui.view_manager_base import ViewManagerBase
from clive.ui.view import ConfigurableView, ReadyView


View = Union[ReadyView, ConfigurableView]

class ViewManager(ViewManagerBase, Rebuildable):
    """
    A root that contains all other components.
    It doesn't define any layout, it just uses the one present in the currently set (active) view.
    Should be created only once.
    """

    def __init__(self) -> None:
        self.__active_view: Optional[View] = None
        super().__init__()

    @property
    def active_view(self) -> View:
        if self.__active_view is None:
            raise ViewException("No view was selected.")

        return self.__active_view

    @active_view.setter
    def active_view(self, value: View) -> None:
        settable = (ConfigurableView, ReadyView, FormView)
        if not isinstance(value, settable):
            raise ViewException(f"Could not set view to `{value}`. It must be an instance of {list(settable)}.")

        self.__active_view = value
        self._rebuild()

    def _rebuild(self) -> None:
        self._root_container.children = [to_container(self.active_view.container)]


view_manager = ViewManager()
