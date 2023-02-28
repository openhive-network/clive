from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget

from clive.ui.widgets.select.select_item import SelectItem
from clive.ui.widgets.select.select_list import _SelectList
from clive.ui.widgets.select.select_list_search_input import _SelectListSearchInput

if TYPE_CHECKING:
    from textual import events

    from clive.ui.widgets.select.select_item import SelectItemType


class Select(Widget, can_focus=True):
    """
    A select widget with a drop-down.
    Modified version of: https://github.com/mitosch/textual-select
    """

    # TODO: validate given items (list of dicts not like value, text)
    # OPTIMIZE: when empty, show dimmed text (e.g. "no entries")
    # OPTIMIZE: get rid of self.app.query_one(self.list_mount)
    # OPTIMIZE: option: individual height
    # OPTIMIZE: mini-bug: resize not nice when opened (edge case...)
    # OPTIMIZE: auto-select by key-press without search? (hard)

    DEFAULT_CSS = """
    Select {
      background: $boost;
      color: $text;
      padding: 0 2;
      border: tall $background;
      height: 1;
      min-height: 1;
    }
    Select:focus {
      border: tall $accent;
    }
    """

    MIN_AMOUNT_OF_ITEMS: Final[int] = 2

    selected: reactive[SelectItem | None] = reactive(None, layout=True, init=False)

    def __init__(
        self,
        items: list[SelectItem],
        list_mount: str,
        *,
        search: bool = False,
        selected: int | SelectItemType | SelectItem | None = None,
        placeholder: str = "",
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id_, classes=classes)

        self.__items = items
        self.__assert_min_amount_of_items()
        self.__list_mount = list_mount
        self.__search = search

        self.__retrieve_selected(selected)
        self.__placeholder = placeholder

        self.__classes = classes

        self.__select_list: _SelectList = _SelectList(
            select=self,
            items=self.__items,
            classes=self.__classes,
        )

        self.text = self.selected.text if self.selected is not None else ""

    @property
    def select_list(self) -> _SelectList:
        return self.__select_list

    @property
    def search(self) -> bool:
        return self.__search

    def render(self) -> str:
        chevron = "\u25bc"
        text_space = max(0, self.content_size.width - 2)

        text = self.selected.text if self.selected is not None else self.__placeholder or self.text

        if len(text) > text_space:
            text = text[0:text_space]

        return f"{text:{text_space}} {chevron}"

    def on_mount(self) -> None:
        # NOTE: mount-point for list is mandatory for the time beeing
        #
        # possibility to automatically find mount point of the drop-down list:
        # * find an ancestor, which's height is greater than the lists height
        # * if it fails (screen size too small, container too small), take
        #   screen container
        #
        # pseudo code:

        # for ancestor in self.ancestors:
        #     if issubclass(ancestor.__class__, Widget):
        #           it's a normal widget
        #     else if issubclass(..., App):
        #           use this child...

        self.app.query_one(self.__list_mount).mount(self.select_list)

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.__show_select_list()
        elif event.key == "down":
            self.__select_list.select_next()
        elif event.key == "up":
            self.__select_list.select_previous()

    def on_click(self) -> None:
        self.__show_select_list()

    class Changed(Message, bubble=True):
        def __init__(self, sender: Select, selected: SelectItem | None) -> None:
            super().__init__(sender)
            self.selected = selected

    async def watch_selected(self, selected: SelectItem | None) -> None:
        if selected is None:
            self.text = ""
            self.__select_list.select_list_view.index = 0
        else:
            self.text = selected.text

        self.refresh(layout=True)
        await self.post_message(self.Changed(self, selected))

    def __assert_min_amount_of_items(self) -> None:
        if len(self.__items) < self.MIN_AMOUNT_OF_ITEMS:
            raise ValueError(f"At least {self.MIN_AMOUNT_OF_ITEMS} items are required to use {self}.")

    def __retrieve_selected(self, selected: int | SelectItem | None) -> None:
        if isinstance(selected, int):
            self.selected = self.__items[selected]
        elif isinstance(selected, SelectItem):
            self.selected = selected
        elif selected is not None:
            self.selected = next(filter(lambda item: item.value == selected, self.__items), None)

    def __show_select_list(self) -> None:
        self.__select_list.select_list_view.index = (
            self.__items.index(self.selected) if self.selected is not None else 0
        )

        mount_widget = self.app.query_one(self.__list_mount)

        self.select_list.display = True
        self.select_list.styles.width = self.outer_size.width

        # OPTIMIZE: this could be done more configurable
        default_height = 5 if not self.__search else 8
        self.select_list.styles.height = default_height
        self.select_list.styles.min_height = default_height

        # calculate the offset by using the mount-point's offset:
        # setting the offset directly from self.region (Select widget)
        # has the header *not* included, therefore we need to subtract
        # the mount-point's offset.
        #
        # further explanation (or assumption):
        # it looks like the mount point has a relative offset, e.g. below
        # the header. setting the offset of the list directly seams to be
        # absolute.

        self.select_list.offset = self.region.offset - mount_widget.content_region.offset

        if self.__search:
            self.select_list.query_one("_SelectListSearchInput", _SelectListSearchInput).focus()
        else:
            self.select_list.query("ListView").first().focus()
