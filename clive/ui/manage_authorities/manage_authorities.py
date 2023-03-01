from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container
from textual.widgets import Button, Static

from clive.ui.manage_authorities.edit_authority import EditAuthority
from clive.ui.manage_authorities.new_authority import NewAuthority
from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.big_title import BigTitle
from clive.ui.widgets.clive_widget import CliveWidget
from clive.ui.widgets.dynamic_label import DynamicLabel

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.storage.mock_database import PrivateKey, ProfileData
    from clive.ui.manage_authorities.widgets.authority_form import AuthorityForm


class DynamicColumn(DynamicLabel):
    """Column with dynamic content"""


class StaticColumn(Static):
    """Column with static content"""


class ColumnLayout(Static):
    """This class holds column order"""


odd = "OddColumn"
even = "EvenColumn"


class Authority(ColumnLayout, CliveWidget):
    def __init__(self, authority: PrivateKey) -> None:
        self.__authority = authority
        super().__init__()

    def compose(self) -> ComposeResult:
        def authority_index(profile_data: ProfileData) -> str:
            if self.__authority in profile_data.active_account.keys:
                return f"{profile_data.active_account.keys.index(self.__authority) + 1}."
            return "⌛"

        yield DynamicColumn(self.app, "profile_data", authority_index, id_="authority_row_number", classes=even)
        yield DynamicColumn(
            self.app, "profile_data", lambda _: self.__authority.key_name, id_="authority_name", classes=odd
        )
        yield StaticColumn("🔐 " + self.__authority.__class__.__name__, id="authority_type", classes=even)
        yield Button("✏️", id="edit_authority_button", classes=odd)
        yield Button("🗑️", id="remove_authority_button", classes=even)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "remove_authority_button":
            self.app.profile_data.active_account.keys.remove(self.__authority)
            self.add_class("deleted")
            self.remove()
        if event.button.id == "edit_authority_button":
            self.app.push_screen(EditAuthority(self.__authority))


class AuthorityHeader(ColumnLayout):
    def compose(self) -> ComposeResult:
        yield StaticColumn("No.", id="authority_row_number", classes=even)
        yield StaticColumn("Authority Name", id="authority_name", classes=odd)
        yield StaticColumn("Authority Type", id="authority_type", classes=even)
        yield StaticColumn("Edit", classes=odd)
        yield StaticColumn("Delete", classes=even)


class AuthorityTitle(Static):
    def compose(self) -> ComposeResult:
        yield BigTitle("authorities", id="authorities_title_label")
        yield Button("✨ Add New Authority", id="add_authority_button")


class ManageAuthorities(BaseScreen):
    def create_main_panel(self) -> ComposeResult:
        self.__mount_point = Container()
        with self.__mount_point:
            yield AuthorityTitle()
            yield AuthorityHeader()
            for key in self.app.profile_data.active_account.keys:
                yield Authority(key)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "add_authority_button":
            na = NewAuthority()
            self.app.push_screen(na)

    def on_authority_form_saved(self, event: AuthorityForm.Saved) -> None:
        self.__mount_point.mount(Authority(event.authority), self.__mount_point)
        self.app.pop_screen()

    def on_authority_form_canceled(self, _: AuthorityForm.Canceled) -> None:
        self.app.pop_screen()
