from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.reactive import watch
from textual.widgets import Label

if TYPE_CHECKING:
    from textual.reactive import Reactable


class DynamicLabel(Label):
    """A label that can be updated dynamically when a reactive variable changes."""

    def __init__(self, obj_to_watch: Reactable, attribute_name: str, *, prefix: str = "") -> None:
        super().__init__("DynamicLabel was not updated!")
        self.__obj_to_watch = obj_to_watch
        self.__attribute_name = attribute_name
        self.__prefix = prefix

    def on_mount(self) -> None:
        watch(self.__obj_to_watch, self.__attribute_name, self.on_attribute_changed)

    def on_attribute_changed(self, value: Any) -> None:
        self.update(f"{self.__prefix}{value}")
