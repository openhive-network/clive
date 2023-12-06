from __future__ import annotations

from textual.containers import ScrollableContainer

from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.big_title import BigTitle


class DialogContainer(ScrollableContainer, can_focus=False):
    """A container for dialog-like looking widgets. Content stored inside this container will be centered."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: str = "", *, id_: str | None = None, classes: str | None = None) -> None:
        self.__title = title
        super().__init__(id=id_, classes=classes)

    def on_mount(self) -> None:
        if self.__title:
            self.mount(BigTitle(self.__title), before=0)
