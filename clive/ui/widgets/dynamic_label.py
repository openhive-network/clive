from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.widgets import Label

if TYPE_CHECKING:
    from collections.abc import Callable

    from textual.reactive import Reactable


class DynamicLabel(Label):
    """A label that can be updated dynamically when a reactive variable changes."""

    def __init__(
        self,
        obj_to_watch: Reactable,
        attribute_name: str,
        callback: Callable[[Any], Any],
        *,
        prefix: str = "",
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__("DynamicLabel was not updated!", id=id_, classes=classes)
        self.__obj_to_watch = obj_to_watch
        self.__attribute_name = attribute_name
        self.__callback = callback
        self.__prefix = prefix

    def on_mount(self) -> None:
        self.watch(self.__obj_to_watch, self.__attribute_name, self.on_attribute_changed)

    def on_attribute_changed(self, attribute: Any) -> None:
        self.update(f"{self.__prefix}{self.__callback(attribute)}")
