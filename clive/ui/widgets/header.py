from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import Header as TextualHeader
from textual.widgets._header import HeaderClock, HeaderTitle
from textual.widgets._header import HeaderIcon as TextualHeaderIcon

from clive.storage.mock_database import mock_db
from clive.ui.widgets.clive_widget import CliveWidget
from clive.ui.widgets.titled_label import TitledLabel

if TYPE_CHECKING:
    from textual import events
    from textual.app import ComposeResult


class HeaderIcon(TextualHeaderIcon):
    def __init__(self) -> None:
        super().__init__(id="icon")

    def on_mount(self) -> None:
        self.watch(self.app, "header_expanded", self.on_header_expanded)  # type: ignore # https://github.com/Textualize/textual/issues/1805

    def on_header_expanded(self, expanded: bool) -> None:
        self.icon = "-" if expanded else "+"


class Header(TextualHeader, CliveWidget):
    def __init__(self) -> None:
        super().__init__()

    def on_mount(self) -> None:
        self.watch(self.app, "header_expanded", self.on_header_expanded)  # type: ignore # https://github.com/Textualize/textual/issues/1805

    def compose(self) -> ComposeResult:
        yield HeaderIcon()
        yield Horizontal(
            TitledLabel("Profile", "Account", id_="profile-label"),
            HeaderTitle(),
            TitledLabel("Mode", "ACTIVE", id_="mode-label"),
        )
        yield HeaderClock()
        yield TitledLabel("node address", obj_to_watch=mock_db, attribute_name="node_address")

    def on_click(self, event: events.Click) -> None:  # type: ignore
        event.prevent_default()
        self.app.header_expanded = not self.app.header_expanded

    def on_header_expanded(self, expanded: bool) -> None:
        self.add_class("-tall") if expanded else self.remove_class("-tall")
