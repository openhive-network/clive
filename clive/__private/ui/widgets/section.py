from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container

from clive.__private.ui.widgets.scrolling import ScrollablePart, ScrollablePartFocusable
from clive.__private.ui.widgets.section_title import SectionTitle

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widget import Widget


class SectionBody(Container):
    """
    A container for the body of the section.

    Attributes:
        DEFAULT_CSS: The default CSS styles for the widget.
    """

    DEFAULT_CSS = """
    SectionBody {
        background: $panel;
        height: auto;
        padding: 1;
    }
    """


class Section(Container):
    """
    Container with predefined background padding and optionally added title.

    Attributes:
        DEFAULT_CSS: The default CSS styles for the widget.

    Args:
        title: The title of the section, if any.
        id_: The ID of the section widget.
        classes: Additional CSS classes for the section.
    """

    DEFAULT_CSS = """
    Section {
        height: auto;
    }
    """

    def __init__(self, title: str | None = None, id_: str | None = None, classes: str | None = None) -> None:
        super().__init__(id=id_, classes=classes)
        self._title = title
        self._section_children: list[Widget] = []

    def compose(self) -> ComposeResult:
        if self._title:
            yield SectionTitle(self._title)
        with SectionBody():
            yield from self._section_children

    def compose_add_child(self, widget: Widget) -> None:
        self._section_children.append(widget)


class SectionScrollable(Section):
    """Scrollable version of section container."""

    DEFAULT_CSS = """
    SectionScrollable {
        height: 1fr;
    }
    """

    def __init__(
        self, title: str | None = None, id_: str | None = None, classes: str | None = None, *, focusable: bool = False
    ) -> None:
        super().__init__(title=title, id_=id_, classes=classes)
        self._focusable = focusable

    def compose(self) -> ComposeResult:
        with ScrollablePartFocusable() if self._focusable else ScrollablePart():
            if self._title:
                yield SectionTitle(self._title)
            with SectionBody():
                yield from self._section_children
