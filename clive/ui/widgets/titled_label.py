from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Label

from clive.ui.widgets.clive_widget import CliveWidget
from clive.ui.widgets.dynamic_label import DynamicLabel

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.app import ComposeResult
    from textual.reactive import Reactable


class TitledLabel(CliveWidget):
    """
    A label with a title and a value.
    The value can be updated dynamically if :obj_to_watch: and :attribute_name: is given.
    When :value: is provided with both of the mentioned parameters, it will be used as a prefix for the dynamic value.
    """

    def __init__(
        self,
        title: RenderableType,
        value: str = "",
        *,
        obj_to_watch: Reactable | None = None,
        attribute_name: str | None = None,
        id_: str | None = None,
    ) -> None:
        super().__init__(id=id_)
        self.__title = title
        self.__value = value

        self.__value_label = (
            DynamicLabel(obj_to_watch, attribute_name, prefix=self.__formatted_value(), id_="value")
            if obj_to_watch and attribute_name
            else Label(self.__formatted_value(), id="value")
        )

    def compose(self) -> ComposeResult:
        yield Label(f"{self.__title}:", id="title")
        yield self.__value_label

    def __formatted_value(self) -> str:
        return f" {self.__value}"
