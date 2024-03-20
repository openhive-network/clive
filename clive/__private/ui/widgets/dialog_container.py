from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container, ScrollableContainer

from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.big_title import BigTitle

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widget import Widget


class DialogBody(ScrollableContainer, can_focus=False):
    """A container for the body of the dialog. It will be scrollable if needed."""


class DialogContainer(Container, can_focus=False):
    """A container for dialog-like looking widgets. Content stored inside this container will be centered."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: str = "", *, id_: str | None = None, classes: str | None = None) -> None:
        self.__title = title
        super().__init__(id=id_, classes=classes)
        self._dialog_children: list[Widget] = []

    def compose(self) -> ComposeResult:
        with DialogBody():
            yield from self._dialog_children

    def on_mount(self) -> None:
        if self.__title:
            self.query_one(DialogBody).mount(BigTitle(self.__title), before=0)

    def compose_add_child(self, widget: Widget) -> None:
        self._dialog_children.append(widget)
