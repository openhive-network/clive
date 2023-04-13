from __future__ import annotations

from typing import TYPE_CHECKING, Generic

from textual.widget import Widget
from textual.widgets import Static

from clive.__private.ui.widgets.select.select import Select
from clive.__private.ui.widgets.select.select_item import SelectItem, SelectItemValueType

if TYPE_CHECKING:
    from textual.app import ComposeResult


class SafeSelect(Widget, Generic[SelectItemValueType]):
    DEFAULT_CSS = """
    SafeSelect {
        min-height: 3;
        align: center middle;
    }

    SafeSelect .-empty-list {
        color: $error-lighten-1;
    }
    """

    def __init__(
        self,
        items: list[SelectItem[SelectItemValueType]],
        list_mount: str | Widget,
        *,
        search: bool = False,
        selected: int | SelectItemValueType | SelectItem[SelectItemValueType] | None = None,
        placeholder: str = "",
        empty_string: str = "nothing to choose",
        id_: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        self.__selected: SelectItem[SelectItemValueType] | None = None
        if len(items) >= Select.MIN_AMOUNT_OF_ITEMS:
            self.__content: Select[SelectItemValueType] | Static = Select(
                items, list_mount, search=search, selected=selected, placeholder=placeholder
            )
        elif len(items) == 0:
            self.__content = Static(empty_string, classes="-empty-list")
        else:  # if len(items) == 1
            self.__selected = items[0]
            self.__content = Static(self.__selected.text)
        super().__init__(id=id_, classes=classes, disabled=disabled)

    @property
    def selected(self) -> SelectItem[SelectItemValueType]:
        if isinstance(self.__content, Static):
            assert self.__selected is not None
            return self.__selected
        if isinstance(self.__content, Select):
            return self.__content.selected
        raise ValueError(f"unknown self.__content type: {type(self.__content).__name__}", self.__content)

    def compose(self) -> ComposeResult:
        yield self.__content
