from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton
from clive.__private.ui.widgets.dynamic_widgets.dynamic_widget import (
    DynamicWidget,
    DynamicWidgetCallbackType,
    DynamicWidgetFirstTryCallbackType,
)

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.reactive import Reactable

    from clive.__private.ui.widgets.buttons.clive_button import CliveButtonVariant


class DynamicOneLineButton(DynamicWidget[OneLineButton]):
    can_focus = False

    def __init__(
        self,
        obj_to_watch: Reactable,
        attribute_name: str,
        callback: DynamicWidgetCallbackType,
        *,
        first_try_callback: DynamicWidgetFirstTryCallbackType = lambda: True,
        variant: CliveButtonVariant = "primary",
        prefix: str = "",
        init: bool = True,
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        self._variant = variant
        super().__init__(
            obj_to_watch,
            attribute_name,
            callback,
            first_try_callback=first_try_callback,
            prefix=prefix,
            init=init,
            id_=id_,
            classes=classes,
        )

    def update_widget_label(self, result: str) -> None:
        if result != self._widget.label:
            self._widget.label = f"{self._prefix}{result}"

    def create_widget(self) -> OneLineButton:
        _button = OneLineButton("loading...", self._variant)
        _button.can_focus = False
        return _button

    @property
    def renderable(self) -> TextType:
        return self._widget.label
