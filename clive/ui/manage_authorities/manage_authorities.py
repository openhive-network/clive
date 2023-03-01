from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Final

from textual.widgets import Button, Static

from clive.storage.mock_database import PrivateKey, ProfileData
from clive.ui.widgets.clive_widget import CliveWidget
from clive.ui.manage_authorities.edit_authority import EditAuthorities
from clive.ui.manage_authorities.new_authority import NewAuthority
from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.big_title import BigTitle
from clive.ui.widgets.dynamic_label import DynamicLabel

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.ui.app import Clive


class DynamicColumn(DynamicLabel):
    """Column with dynamic content"""


class StaticColumn(Static):
    """Column with static content"""


class ColumnLayout(Static):
    """This class holds column order"""


odd: Final[Dict[str, str]] = {"classes": "OddColumn"}
even: Final[Dict[str, str]] = {"classes": "EvenColumn"}


class Authority(ColumnLayout, CliveWidget):
    def __init__(self, authority: PrivateKey) -> None:
        self.__authority = authority
        super().__init__()

    def compose(self) -> ComposeResult:
        def authority_index(profile_data: ProfileData) -> str:
            if self.__authority in profile_data.active_account.keys:
                return f"{profile_data.active_account.keys.index(self.__authority) + 1}."
            return "⌛"

        yield DynamicColumn(self.app, "profile_data", authority_index, id_="authority_row_number", **even)
        yield DynamicColumn(self.app, "profile_data", lambda _: self.__authority.key_name, id_="authority_name", **odd)
        yield StaticColumn("🔐 " + self.__authority.__class__.__name__, id="authority_type", **even)
        yield Button("✏️", id="edit_authority_button", **odd)
        yield Button("🗑️", id="remove_authority_button", **even)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "remove_authority_button":
            self.app.profile_data.active_account.keys.remove(self.__authority)
            self.add_class("deleted")
            self.remove()
        if event.button.id == "edit_authority_button":
            self.__edit_authority_view()

    def __edit_authority_view(self) -> None:
        self.app.push_screen(EditAuthorities(self.__authority, self.__update_authority))

    def __update_authority(self) -> None:
        self.app.update_reactive("profile_data")


class AuthorityHeader(ColumnLayout):
    def compose(self) -> ComposeResult:
        yield StaticColumn("No.", id="authority_row_number", **even)
        yield StaticColumn("Authority Name", id="authority_name", **odd)
        yield StaticColumn("Authority Type", id="authority_type", **even)
        yield StaticColumn("Edit", **odd)
        yield StaticColumn("Delete", **even)


class AuthorityTitle(Static):
    def compose(self) -> ComposeResult:
        yield BigTitle("authorities", id="authorities_title_label")
        yield Button("✨ Add New Authority", id="add_authority_button")


class ManageAuthorities(BaseScreen):
    def create_main_panel(self) -> ComposeResult:
        yield AuthorityTitle()
        self.__last_widget: Any = AuthorityHeader()
        yield self.__last_widget

        for key in self.app.profile_data.active_account.keys:
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
                    self.app.profile_data.active_account.keys.append(pv_key)

                    auth = Authority(pv_key)
                    self.mount(auth, self.__last_widget)

                    self.__last_widget = auth

            self.app.push_screen(NewAuthority(pv_key, __create_new_authority_callback))
