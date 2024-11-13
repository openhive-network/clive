from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.buttons import OneLineButton
from clive.__private.ui.widgets.dynamic_widgets.dynamic_widget import (
    DynamicWidget,
    DynamicWidgetFirstTryCallbackType,
    WatchLikeCallbackType,
)

if TYPE_CHECKING:
    from textual.reactive import Reactable

    from clive.__private.ui.widgets.buttons.clive_button import CliveButtonVariant


DynamicOneLineButtonCallbackType = WatchLikeCallbackType[str]


class DynamicOneLineButton(DynamicWidget[OneLineButton, str]):
    def __init__(
        self,
        obj_to_watch: Reactable,
        attribute_name: str,
        callback: DynamicOneLineButtonCallbackType,
        *,
        first_try_callback: DynamicWidgetFirstTryCallbackType = lambda: True,
        variant: CliveButtonVariant = "loading-variant",
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
            init=init,
            id_=id_,
            classes=classes,
        )

    def _create_widget(self) -> OneLineButton:
        return OneLineButton("loading...", self._variant)

    def _update_widget_state(self, result: str) -> None:
        if self._widget.variant == "loading-variant":
            self._widget.variant = "primary"

        if result != self._widget.label:
            self._widget.update(result)


class DynamicOneLineButtonUnfocusable(DynamicOneLineButton):
    def _create_widget(self) -> OneLineButton:
        button = super()._create_widget()
        button.can_focus = False
        return button
