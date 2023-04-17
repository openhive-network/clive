from __future__ import annotations

from typing import TYPE_CHECKING, Generic

from textual.widget import Widget
from textual.widgets import Static

from clive.__private.ui.widgets.select.select import Select
from clive.__private.ui.widgets.select.select_item import SelectItem, SelectItemValueType
from clive.exceptions import NoItemSelectedError

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
        super().__init__(id=id_, classes=classes, disabled=disabled)

        self.__selected: SelectItem[SelectItemValueType] | None = None
        self.__content: Select[SelectItemValueType] | Static = Static(empty_string, classes="-empty-list")

        if len(items) >= Select.MIN_AMOUNT_OF_ITEMS:
            self.__content = Select(items, list_mount, search=search, selected=selected, placeholder=placeholder)
        elif items:
            self.__selected = items[0]
            self.__content = Static(self.__selected.text)

    @property
    def selected(self) -> SelectItem[SelectItemValueType]:
        if self.__selected is None:
            raise NoItemSelectedError(f"No item is selected yet from {self}.")
        return self.__selected

    def compose(self) -> ComposeResult:
        yield self.__content
