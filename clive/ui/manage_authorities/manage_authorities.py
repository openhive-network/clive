from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.widgets import Button, Static

from clive.storage.mock_database import PrivateKey
from clive.ui.manage_authorities.edit_authority import EditAuthorities
from clive.ui.manage_authorities.new_authority import NewAuthority
from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.big_title import BigTitle
from clive.ui.widgets.dynamic_label import DynamicLabel

if TYPE_CHECKING:
    from textual.app import ComposeResult


class OddColumn(Static):
    """Odd column class"""


class DynamicColumn(DynamicLabel):
    pass


class EvenColumn(Static):
    """Even column class"""


class ColumnLayout(Static):
    """This class holds column order"""


class Authority(ColumnLayout):
    def __init__(self, authority: PrivateKey, number: int) -> None:
        self.__authority = authority
        self.__number = number
        super().__init__()

    def compose(self) -> ComposeResult:
        from clive.ui.app import clive_app

        yield EvenColumn(f"{self.__number}", id="authority_row_number")
        auth_name = DynamicColumn(clive_app, "profile_data", lambda _: self.__authority.key_name, id_="authority_name")
        auth_name.add_class("OddColumn")
        yield auth_name
        yield EvenColumn("🔐 " + self.__authority.__class__.__name__, id="authority_type")
        yield Button("✏️", id="edit_authority_button")
        yield Button("🗑️", id="remove_authority_button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "remove_authority_button":
            from clive.ui.app import clive_app

            clive_app.profile_data.active_account.keys.remove(self.__authority)
            self.add_class("deleted")
        if event.button.id == "edit_authority_button":
            self.__edit_authority_view()
        else:
            self.__go_to_detailed_view()

    def __go_to_detailed_view(self) -> None:
        pass

    def __edit_authority_view(self) -> None:
        self.app.push_screen(EditAuthorities(self.__authority, self.__update_authority))

    def __update_authority(self) -> None:
        from clive.ui.app import clive_app

        clive_app.update_reactive("profile_data")


class AuthorityHeader(ColumnLayout):
    def compose(self) -> ComposeResult:
        yield EvenColumn("No.", id="authority_row_number")
        yield OddColumn("Authority Name", id="authority_name")
        yield EvenColumn("Authority Type", id="authority_type")
        yield OddColumn("Edit")
        yield EvenColumn("Delete")


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

        self.__last_id = 0
        for i, key in enumerate(clive_app.profile_data.active_account.keys):
            self.__last_id += 1

            auth = Authority(key, self.__last_id)

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
                    self.__last_id += 1

                    auth = Authority(pv_key, self.__last_id)
                    self.mount(auth, self.__last_widget)

                    self.__last_widget = auth

            self.app.push_screen(NewAuthority(pv_key, __create_new_authority_callback))
