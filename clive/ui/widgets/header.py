from __future__ import annotations

from typing import TYPE_CHECKING

from textual.reactive import watch
from textual.widgets import Header as TextualHeader
from textual.widgets._header import HeaderClock, HeaderTitle
from textual.widgets._header import HeaderIcon as TextualHeaderIcon

from clive.ui.widgets.titled_label import TitledLabel

if TYPE_CHECKING:
    from textual import events
    from textual.app import ComposeResult

    from clive.ui.app import Clive


class HeaderIcon(TextualHeaderIcon):
    def __init__(self) -> None:
        super().__init__(id="icon")

    def on_mount(self) -> None:
        watch(self.app, "header_expanded", self.on_header_expanded)

    def on_header_expanded(self, expanded: bool) -> None:
        self.icon = "-" if expanded else "+"


class Header(TextualHeader):
    def __init__(self) -> None:
        super().__init__()

    def on_mount(self) -> None:
        watch(self.app, "header_expanded", self.on_header_expanded)

    def compose(self) -> ComposeResult:
        yield HeaderIcon()
        yield HeaderTitle()
        yield HeaderClock()
        yield TitledLabel("node", "https://hive.blog")

    def on_click(self, event: events.Click) -> None:  # type: ignore
        event.prevent_default()

        self.app: Clive
        self.app.header_expanded = not self.app.header_expanded

    def on_header_expanded(self, expanded: bool) -> None:
        self.add_class("-tall") if expanded else self.remove_class("-tall")
