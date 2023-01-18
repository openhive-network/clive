from __future__ import annotations

from abc import ABC

from prompt_toolkit.layout import DynamicContainer

from clive.ui.component import Component


class DynamicComponent(Component, ABC):
    """A component that refreshes (rebuilds) its container automatically during runtime."""

    def __init__(self) -> None:
        super().__init__()
        self._container = DynamicContainer(lambda: self._create_container())
