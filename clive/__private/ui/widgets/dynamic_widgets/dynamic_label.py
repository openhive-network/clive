from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Label

from clive.__private.ui.widgets.dynamic_widgets.dynamic_widget import (
    DynamicWidget,
    DynamicWidgetFirstTryCallbackType,
    WatchLikeCallbackType,
)

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.reactive import Reactable

DynamicLabelCallbackType = WatchLikeCallbackType[str]


class DynamicLabel(DynamicWidget[Label, str]):
    def __init__(
        self,
        obj_to_watch: Reactable,
        attribute_name: str,
        callback: DynamicLabelCallbackType,
        *,
        first_try_callback: DynamicWidgetFirstTryCallbackType = lambda: True,
        prefix: str = "",
        init: bool = True,
        id_: str | None = None,
        classes: str | None = None,
        shrink: bool = False,
    ) -> None:
        self._shrink = shrink
        self._prefix = prefix
        super().__init__(
            obj_to_watch,
            attribute_name,
            callback,
            first_try_callback=first_try_callback,
            init=init,
            id_=id_,
            classes=classes,
        )

    @property
    def renderable(self) -> RenderableType:
        return self._widget.renderable

    def _update_widget_state(self, result: str) -> None:
        if result != self.renderable:
            self._widget.update(f"{self._prefix}{result}")

    def _create_widget(self) -> Label:
        return Label("loading...", shrink=self._shrink)
