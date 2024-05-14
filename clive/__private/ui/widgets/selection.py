from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container

from clive.__private.ui.widgets.section_title import SectionTitle

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widget import Widget


class SelectionBody(Container):
    """A container for the body of the selection."""


class Selection(Container):
    """Container with predefined background padding and optionally added SectionTitle."""

    DEFAULT_CSS = """
    Selection {
        SelectionBody {
            background: $panel;
            padding: 1;
            height: auto;
        }
    }
    """

    def __init__(self, title: str | None = None, id_: str | None = None, classes: str | None = None):
        self._title = title
        super().__init__(id=id_, classes=classes)
        self._selection_children: list[Widget] = []

    def compose(self) -> ComposeResult:
        if self._title:
            yield SectionTitle(self._title)
        with SelectionBody():
            yield from self._selection_children

    def compose_add_child(self, widget: Widget) -> None:
        self._selection_children.append(widget)
