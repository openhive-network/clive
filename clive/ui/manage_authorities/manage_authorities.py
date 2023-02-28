from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.widgets import Button, Static

from clive.storage.mock_database import PrivateKey, ProfileData
from clive.ui.manage_authorities.edit_authority import EditAuthorities
from clive.ui.manage_authorities.new_authority import NewAuthority
from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.big_title import BigTitle
from clive.ui.widgets.dynamic_label import DynamicLabel

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widget import Widget

    from clive.ui.app import Clive


class DynamicColumn(DynamicLabel):
    """Column with dynamic content"""


class StaticColumn(Static):
    """Column with static content"""


class ColumnLayout(Static):
    """This class holds column order"""


def odd(widget: Widget) -> Widget:
    widget.add_class("OddColumn")
    return widget


def even(widget: Widget) -> Widget:
    widget.add_class("EvenColumn")
    return widget


class Authority(ColumnLayout):
    def __init__(self, authority: PrivateKey) -> None:
        self.__authority = authority
        super().__init__()

    def compose(self) -> ComposeResult:
        def authority_index(profile_data: ProfileData) -> str:
            return f"{profile_data.active_account.keys.index(self.__authority) + 1}."

        yield even(DynamicColumn(self.__clive, "profile_data", authority_index, id_="authority_row_number"))
        yield odd(
            DynamicColumn(self.__clive, "profile_data", lambda _: self.__authority.key_name, id_="authority_name")
        )
        yield even(StaticColumn("🔐 " + self.__authority.__class__.__name__, id="authority_type"))
        yield odd(Button("✏️", id="edit_authority_button"))
        yield even(Button("🗑️", id="remove_authority_button"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "remove_authority_button":
            self.__clive.profile_data.active_account.keys.remove(self.__authority)
            self.add_class("deleted")
        if event.button.id == "edit_authority_button":
            self.__edit_authority_view()

    def __edit_authority_view(self) -> None:
        self.app.push_screen(EditAuthorities(self.__authority, self.__update_authority))

    def __update_authority(self) -> None:
        self.__clive.update_reactive("profile_data")

    @property
    def __clive(self) -> Clive:
        from clive.ui.app import clive_app

        return clive_app


class AuthorityHeader(ColumnLayout):
    def compose(self) -> ComposeResult:
        yield even(StaticColumn("No.", id="authority_row_number"))
        yield odd(StaticColumn("Authority Name", id="authority_name"))
        yield even(StaticColumn("Authority Type", id="authority_type"))
        yield odd(StaticColumn("Edit"))
        yield even(StaticColumn("Delete"))


class AuthorityTitle(Static):
    def compose(self) -> ComposeResult:
        yield BigTitle("authorities", id="authorities_title_label")
        yield Button("✨ Add New Authority", id="add_authority_button")


class ManageAuthorities(BaseScreen):
    def create_main_panel(self) -> ComposeResult:
        yield AuthorityTitle()
        self.__last_widget: Any = AuthorityHeader()
        yield self.__last_widget

        from clive.ui.app import clive_app

        for key in clive_app.profile_data.active_account.keys:
            auth = Authority(key)
            self.__last_widget = auth
            yield auth

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "add_authority_button":
            from clive.ui.app import clive_app

            pv_key = PrivateKey("", "")

            def __create_new_authority_callback() -> None:
                if len(pv_key.key) > 0 and len(pv_key.key_name) > 0:
                    clive_app.profile_data.active_account.keys.append(pv_key)

                    auth = Authority(pv_key)
                    self.mount(auth, self.__last_widget)

                    self.__last_widget = auth

            self.app.push_screen(NewAuthority(pv_key, __create_new_authority_callback))
