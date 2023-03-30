from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Input, Label, ListItem

if TYPE_CHECKING:
    from clive.__private.ui.widgets.select.select_list import _SelectList


class _SelectListSearchInput(Input):
    """Input for searching through the list."""

    DEFAULT_CSS = """
    _SelectListSearchInput {
        border: none;
        background: transparent;
        border-bottom: tall $background;
    }
    _SelectListSearchInput:focus {
        border: none;
        border-bottom: tall $accent;
    }
    """

    def __init__(self, select_list: _SelectList) -> None:
        super().__init__()
        self.__select_list = select_list

    def watch_value(self, value: str) -> None:  # type: ignore[override]
        self.__select_list.select_list_view.clear()
        self.__select_list.items_filtered = []
        for item in self.__select_list.items:
            if value.lower() in item.text.lower():
                self.__select_list.select_list_view.append(ListItem(Label(item.text)))
                self.__select_list.items_filtered.append(item)

    def action_scroll_down(self) -> None:
        self.__select_list.select_list_view.action_cursor_down()

    def action_scroll_up(self) -> None:
        self.__select_list.select_list_view.action_cursor_up()

    def on_blur(self) -> None:
        self.__select_list.display = False
        self.value = ""
