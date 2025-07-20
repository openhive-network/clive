from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container

from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.location_indicator import LocationIndicator
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section_title import SectionTitle

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widget import Widget


class DialogBody(Container):
    """A container for the body of the dialog."""


class DialogContainer(Container, can_focus=False):
    """
    A container for dialog-like looking widgets. Content stored inside this container will be centered.

    Attributes:
        DEFAULT_CSS: Default CSS styles for the dialog container.

    Args:
        big_title: The big title of the dialog, displayed at the top.
        section_title: The title of the section inside the dialog.
        id_: Optional ID for the dialog container.
        classes: Optional CSS classes for the dialog container.
    """

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(
        self, big_title: str = "", section_title: str = "", *, id_: str | None = None, classes: str | None = None
    ) -> None:
        self.__big_title = big_title
        self.__section_title = section_title
        super().__init__(id=id_, classes=classes)
        self._dialog_children: list[Widget] = []

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            if self.__section_title:
                yield SectionTitle(self.__section_title)
            with DialogBody():
                yield from self._dialog_children

    def on_mount(self) -> None:
        if self.__big_title:
            self.query_exactly_one(DialogBody).mount(LocationIndicator(self.__big_title), before=0)

    def compose_add_child(self, widget: Widget) -> None:
        self._dialog_children.append(widget)
