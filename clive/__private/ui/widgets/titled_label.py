from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Label

from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_widgets.dynamic_label import (
    DynamicLabel,
)

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.app import ComposeResult
    from textual.reactive import Reactable

    from clive.__private.ui.widgets.dynamic_widgets.dynamic_label import (
        DynamicLabelCallbackType,
    )
    from clive.__private.ui.widgets.dynamic_widgets.dynamic_widget import (
        DynamicWidgetFirstTryCallbackType,
    )


class TitledLabel(CliveWidget):
    """
    A label with a title and a value.

    The value can be updated dynamically if :obj_to_watch: and :attribute_name: is given.
    When :value: is provided with both of the mentioned parameters, it will be used as a prefix for the dynamic value.
    """

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(
        self,
        title: RenderableType,
        value: str = "",
        *,
        obj_to_watch: Reactable | None = None,
        attribute_name: str | None = None,
        callback: DynamicLabelCallbackType | None = None,
        first_try_callback: DynamicWidgetFirstTryCallbackType = lambda: True,
        init: bool = True,
        id_: str | None = None,
    ) -> None:
        super().__init__(id=id_)
        self.title = title
        self._value = value

        self._value_label: DynamicLabel | Label = (
            DynamicLabel(
                obj_to_watch,
                attribute_name,
                callback,
                prefix=self._formatted_value(),
                first_try_callback=first_try_callback,
                init=init,
                id_="value",
            )
            if obj_to_watch and attribute_name and callback
            else Label(self._formatted_value(), id="value")
        )

    @property
    def value(self) -> RenderableType:
        return self._value_label.renderable

    def compose(self) -> ComposeResult:
        yield Label(f"{self.title}:", id="title")
        yield self._value_label

    def _formatted_value(self) -> str:
        return f" {self._value}"
