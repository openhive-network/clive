from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label, ListItem

from clive.ui.widgets.select.select_list_search_input import _SelectListSearchInput
from clive.ui.widgets.select.select_list_view import _SelectListView

if TYPE_CHECKING:
    from textual import events
    from textual.app import ComposeResult

    from clive.ui.widgets.select.select import Select
    from clive.ui.widgets.select.select_item import SelectItem


class _SelectList(Widget):
    """The dropdown list which is opened at the input."""

    DEFAULT_CSS = """
    _SelectList {
      layer: select;
      background: $boost;
      border: tall $accent;
      display: none;
    }
    _SelectList.--search ListView {
      padding-top: 1;
    }
    _SelectList ListItem {
      background: transparent;
      padding: 0 2;
    }
    _SelectList ListItem:hover {
      background: $boost;
    }
    _SelectList ListView:focus > ListItem.--highlight {
    }
    _SelectList _SelectListSearchInput {
      border: none;
      border-bottom: wide $panel;
    }
    """

    def __init__(
        self,
        select: Select,
        items: list[SelectItem],
        classes: str | None = None,
    ) -> None:
        if select.search:
            # when a search is there, add a class for pad-top the list
            classes = f"{str(classes)} --search"

        super().__init__(classes=classes)

        self.__select = select
        self.items = items
        self.items_filtered = items

        self.__select_list_view = _SelectListView(select_list=self)

    @property
    def select_list_view(self) -> _SelectListView:
        return self.__select_list_view

    def compose(self) -> ComposeResult:
        with Vertical():
            if self.__select.search:
                yield _SelectListSearchInput(select_list=self)

            with self.__select_list_view:
                for item in self.items:
                    yield ListItem(Label(item.text))

    def on_key(self, event: events.Key) -> None:
        # NOTE: the message ListView.Selected has drawbacks, we can't use:
        #   * emitted when opened drop-down list
        #   * not emitted, when enter pressed on the initially highlighted ListItem
        #   * emitted on single click (can be ok, but would close immediately)

        if event.key == "escape":
            self.close()
        elif event.key == "enter":
            self.on_click()
        elif event.key == "tab" or event.key == "shift+tab":
            # Suppress tab (blur) when drop-down is open. Gtk is handling it the same.
            event.prevent_default()

    def select_highlighted_item(self) -> None:
        if self.__select_list_view.index is not None:
            # index can be None, if a search results in no entries => do not change select value in this case
            self.__select.selected = self.items_filtered[self.__select_list_view.index]

    def select_next(self) -> None:
        if self.__select.selected is not None:
            self.__select_list_view.index += 1
        self.select_highlighted_item()

    def select_previous(self) -> None:
        if self.__select.selected is not None:
            self.__select_list_view.index -= 1
        self.select_highlighted_item()

    def on_click(self) -> None:
        self.select_highlighted_item()
        self.close()

    def close(self) -> None:
        self.display = False
        self.__select.focus()
