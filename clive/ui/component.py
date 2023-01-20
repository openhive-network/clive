from __future__ import annotations

from abc import ABC, abstractmethod
from functools import update_wrapper
from typing import Any, Callable, Literal, TypeVar

from prompt_toolkit.layout import AnyContainer

from clive.ui.parented import Parented
from clive.ui.rebuildable import Rebuildable

T = TypeVar("T", bound=Rebuildable)


class Component(Parented[T], Rebuildable, ABC):
    """A component is a part of an application that can be displayed on the screen in another component or view."""

    def __init__(self, parent: T) -> None:
        super().__init__(parent)
        self._on_init()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __repr__(self) -> str:
        return str(self)

    def _on_init(self) -> None:
        self._container = self._create_container()

    @property
    def container(self) -> AnyContainer:
        return self._container

    @abstractmethod
    def _create_container(self) -> AnyContainer:
        """Create a container containing all the elements that define the layout."""

    def _rebuild(self) -> None:
        """Rebuilds the current component and then calls the _rebuild method of its parent to propagate the change."""
        self._container = self._create_container()
        if isinstance(self._parent, Rebuildable):
            self._parent._rebuild()


class ConfigurableComponent(Component[T]):
    def _on_init(self) -> None:
        """
        This method is called in constructor, but this class
        has delayed initialization (to __exit__) so there is
        nothing to do in constructor
        """
        self.__is_editable: bool = False
        self.__is_configured: bool = False

    def __enter__(self):
        self.__is_editable = True
        return self

    def __exit__(self, exception_type: type, exception_value: Any, exception_traceback: Any) -> Literal[False]:
        if exception_value is None:
            self._container = self._create_container()
            self.__is_configured = True

        self.__is_editable = False
        return False


def safe_edit(function: Callable[[Any, Any], None]) -> Callable[[Any, Any], None]:
    def impl(self: Any, value: Any) -> None:
        assert self._ConfigurableComponent__is_editable, "Cannot edit outside `with` statement"
        function(self, value)
        if self._ConfigurableComponent__is_configured:
            self._rebuild()

    return update_wrapper(impl, function)
