from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.ui.component import Component


class View(ABC):
    """Component that can be displayed on its own in the application."""

    def __init__(self, component: Component) -> None:
        self._component = component

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self._component})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def component(self) -> Component:
        return self._component
