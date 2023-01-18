from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.widgets import Label

from clive.exceptions import ViewException
from clive.ui.component import DynamicComponent
from clive.ui.view import View

if TYPE_CHECKING:
    from prompt_toolkit.layout import AnyContainer


class RootComponent(DynamicComponent):
    """A root component that contains all other components. Should be created only once."""

    def __init__(self) -> None:
        self.__view: View | None = None
        self.__default_container = Label(text="No view selected... Loading...")
        super().__init__()

    def _create_container(self) -> AnyContainer:
        return self.__view.container if self.__view else self.__default_container

    @property
    def view(self) -> View | None:
        return self.__view

    @view.setter
    def view(self, value: View) -> None:
        if not isinstance(value, View):
            raise ViewException(f"Could not set view to `{value}`. It must be an instance of `{View}`.")

        self.__view = value


root_component = RootComponent()
