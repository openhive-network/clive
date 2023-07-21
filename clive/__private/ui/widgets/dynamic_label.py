from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.widgets import Label

from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from collections.abc import Callable

    from textual.reactive import Reactable


class DynamicLabel(Label, CliveWidget):
    """A label that can be updated dynamically when a reactive variable changes."""

    def __init__(
        self,
        obj_to_watch: Reactable,
        attribute_name: str,
        callback: Callable[[Any], Any],
        *,
        prefix: str = "",
        init: str | None = None,
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(init if init else "DynamicLabel was not updated!", id=id_, classes=classes)
        self.__obj_to_watch = obj_to_watch
        self.__attribute_name = attribute_name
        self.__callback = callback
        self.__prefix = prefix
        self.__init = init

    def on_mount(self) -> None:
        self.watch(self.__obj_to_watch, self.__attribute_name, self.attribute_changed, init=not bool(self.__init))

    def attribute_changed(self, attribute: Any) -> None:
        self.update(f"{self.__prefix}{self.__callback(attribute)}")
