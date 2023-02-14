from __future__ import annotations

from typing import TYPE_CHECKING

from textual.reactive import watch
from textual.widgets import Label

if TYPE_CHECKING:
    from textual.reactive import Reactable


class DynamicLabel(Label):
    """A label that can be updated dynamically when a reactive variable changes."""

    def __init__(self, obj_to_watch: Reactable, attribute_name: str) -> None:
        super().__init__()
        self.__obj_to_watch = obj_to_watch
        self.__attribute_name = attribute_name

    def on_mount(self) -> None:
        watch(self.__obj_to_watch, self.__attribute_name, lambda value: self.update(str(value)))
