from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import Header as TextualHeader
from textual.widgets._header import HeaderClock, HeaderTitle
from textual.widgets._header import HeaderIcon as TextualHeaderIcon

from clive.ui.widgets.clive_widget import CliveWidget
from clive.ui.widgets.titled_label import TitledLabel

if TYPE_CHECKING:
    from textual import events
    from textual.app import ComposeResult

    from clive.storage.mock_database import ProfileData
    from clive.ui.app_state import AppState


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
        self.watch(self.app, "app_state", self.on_app_state)  # type: ignore # https://github.com/Textualize/textual/issues/1805

    def compose(self) -> ComposeResult:
        yield HeaderIcon()
        with Horizontal(id="bar"):
            yield TitledLabel("Profile", "Account", id_="profile-label")
            yield HeaderTitle()
            yield TitledLabel(
                "Mode",
                obj_to_watch=self.app,
                attribute_name="app_state",
                callback=lambda app_state: app_state.mode,
                id_="mode-label",
            )
        yield HeaderClock()
        yield TitledLabel(
            "node address",
            obj_to_watch=self.app,
            attribute_name="profile_data",
            callback=self.__get_node_address,
            id_="node-address-label",
        )

    def on_click(self, event: events.Click) -> None:  # type: ignore
        event.prevent_default()
        self.app.header_expanded = not self.app.header_expanded

    def on_header_expanded(self, expanded: bool) -> None:
        self.add_class("-tall") if expanded else self.remove_class("-tall")

    def on_app_state(self, app_state: AppState) -> None:
        if app_state.is_active():
            self.add_class("-active")
        else:
            self.remove_class("-active")

    @staticmethod
    def __get_node_address(profile_data: ProfileData) -> str:
        return str(profile_data.node_address)
