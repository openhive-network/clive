from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.message import Message
from textual.widgets import Button, Static

from clive.__private.ui.confirm_with_password.confirm_with_password import ConfirmWithPassword
from clive.__private.ui.manage_authorities.edit_authority import EditAuthority
from clive.__private.ui.manage_authorities.new_authority import NewAuthority
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_screen import CliveScreen
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_label import DynamicLabel
from clive.__private.ui.widgets.notification import Notification
from clive.__private.ui.widgets.view_bag import ViewBag

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.keys import PublicKeyAliased


class DynamicColumn(DynamicLabel):
    """Column with dynamic content."""


class StaticColumn(Static):
    """Column with static content."""


class ColumnLayout(Static):
    """Holds column order."""


class ScrollablePart(ScrollableContainer):
    pass


odd = "OddColumn"
even = "EvenColumn"


class Authority(ColumnLayout, CliveWidget):
    class AuthoritiesChanged(Message):
        """Emitted when authorities have been changed."""

    def __init__(self, index: int, authority: PublicKeyAliased) -> None:
        self.__index = index
        self.__authority = authority
        super().__init__()

    def compose(self) -> ComposeResult:
        yield StaticColumn(str(self.__index + 1), id="authority_row_number", classes=even)
        yield StaticColumn(self.__authority.alias, id="authority_name", classes=odd)
        yield StaticColumn("🔐 " + self.__authority.__class__.__name__, id="authority_type", classes=even)
        yield CliveButton("✏️", id_="edit_authority_button", classes=odd)
        yield CliveButton("🗑️", id_="remove_authority_button", classes=even)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "remove_authority_button":
            self.__remove_authority()
        if event.button.id == "edit_authority_button":
            self.app.push_screen(EditAuthority(self.__authority))

    def __remove_authority(self) -> None:
        @CliveScreen.try_again_after_activation(app=self.app)
        def __on_confirmation_result(result: str) -> None:
            if not result:
                return

            self.app.world.commands.remove_key(password=result, key_to_remove=self.__authority)
            self.app.world.profile_data.working_account.keys.remove(self.__authority)

            Notification(f"Authority `{self.__authority.alias}` was removed.", category="success").show()
            self.app.post_message_to_screen(ManageAuthorities, self.AuthoritiesChanged())

        self.app.push_screen(
            ConfirmWithPassword(
                result_callback=__on_confirmation_result, action_name=f"Remove a `{self.__authority.alias}` key."
            )
        )


class AuthorityHeader(ColumnLayout):
    def compose(self) -> ComposeResult:
        yield StaticColumn("No.", id="authority_row_number", classes=even)
        yield StaticColumn("Authority Name", id="authority_name", classes=odd)
        yield StaticColumn("Authority Type", id="authority_type", classes=even)
        yield StaticColumn("Edit", classes=odd)
        yield StaticColumn("Delete", classes=even)


class ManageAuthorities(BaseScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "new_authority", "New authority"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.__scrollable_part = ScrollablePart()

    def create_main_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("authorities")
            yield AuthorityHeader()
            with self.__scrollable_part:
                for idx, key in enumerate(self.app.world.profile_data.working_account.keys):
                    yield Authority(idx, key)

    def action_new_authority(self) -> None:
        self.app.push_screen(NewAuthority())

    def on_authority_form_authorities_changed(self) -> None:
        self.__rebuild_authorities()

    def on_authority_authorities_changed(self) -> None:
        self.__rebuild_authorities()

    def __rebuild_authorities(self) -> None:
        self.query(Authority).remove()

        for idx, key in enumerate(self.app.world.profile_data.working_account.keys):
            self.__scrollable_part.mount(Authority(idx, key))
