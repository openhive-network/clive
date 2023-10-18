from __future__ import annotations

from inspect import isawaitable
from typing import TYPE_CHECKING, Any

from textual.widgets import Label

from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from collections.abc import Callable

    from textual.app import ComposeResult
    from textual.reactive import Reactable


class DynamicLabel(CliveWidget):
    """A label that can be updated dynamically when a reactive variable changes."""

    DEFAULT_CSS = """
    DynamicLabel {
        height: auto;
        width: auto;
    }

    DynamicLabel LoadingIndicator {
        min-height: 1;
        min-width: 5;
    }
    """

    def __init__(
        self,
        obj_to_watch: Reactable,
        attribute_name: str,
        callback: Callable[[Any], Any],
        *,
        prefix: str = "",
        shrink: bool = False,
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id_, classes=classes)

        self.__label = Label("loading...", shrink=shrink)
        self.__label.loading = True

        self.__obj_to_watch = obj_to_watch
        self.__attribute_name = attribute_name
        self.__callback = callback
        self.__prefix = prefix

    def on_mount(self) -> None:
        def delegate_work(attribute: Any) -> None:
            self.run_worker(self.attribute_changed(attribute))

        self.watch(self.__obj_to_watch, self.__attribute_name, delegate_work)

    def compose(self) -> ComposeResult:
        yield self.__label

    async def attribute_changed(self, attribute: Any) -> None:
        value = self.__callback(attribute)
        if isawaitable(value):
            value = await value
        if value != self.__label.renderable:
            self.__label.update(f"{self.__prefix}{value}")
        self.__loading_done()

    def __loading_done(self) -> None:
        self.__label.loading = False
