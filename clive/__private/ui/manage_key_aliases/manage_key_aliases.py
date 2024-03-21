from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.message import Message
from textual.widgets import Static

from clive.__private.ui.confirm_with_password.confirm_with_password import ConfirmWithPassword
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.manage_key_aliases.edit_key_alias import EditKeyAlias
from clive.__private.ui.manage_key_aliases.new_key_alias import NewKeyAlias
from clive.__private.ui.manage_key_aliases.widgets.key_alias_form import KeyAliasForm
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_screen import CliveScreen
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_label import DynamicLabel
from clive.__private.ui.widgets.scrolling import ScrollablePart

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.keys import PublicKeyAliased


class DynamicColumn(DynamicLabel):
    """Column with dynamic content."""


class StaticColumn(Static):
    """Column with static content."""


class ColumnLayout(Static):
    """Holds column order."""


odd = "-odd"
even = "-even"


class KeyAlias(ColumnLayout, CliveWidget):
    class Changed(Message):
        """Emitted when key alias have been changed."""

    def __init__(self, index: int, public_key: PublicKeyAliased) -> None:
        self.__index = index
        self.__public_key = public_key
        super().__init__()

    def compose(self) -> ComposeResult:
        yield StaticColumn(str(self.__index + 1), id="key-alias-row-number", classes=even)
        yield StaticColumn(self.__public_key.alias, id="key-alias-name", classes=odd)
        yield StaticColumn(self.__public_key.value, id="key-alias-public-key", classes=even)
        yield CliveButton("Edit", id_="edit-key-alias-button")
        yield CliveButton("Remove", variant="error", id_="remove-key-alias-button")

    @on(CliveButton.Pressed, "#edit-key-alias-button")
    def push_edit_key_alias_screen(self) -> None:
        self.app.push_screen(EditKeyAlias(self.__public_key))

    @on(CliveButton.Pressed, "#remove-key-alias-button")
    async def remove_key_alias(self) -> None:
        @CliveScreen.try_again_after_activation(app=self.app)
        async def __on_confirmation_result(result: str) -> None:
            if not result:
                return

            self.app.world.profile_data.working_account.keys.remove(self.__public_key)

            self.notify(f"Key alias `{self.__public_key.alias}` was removed.")
            self.app.post_message_to_screen(ManageKeyAliases, self.Changed())

        self.app.push_screen(
            ConfirmWithPassword(
                result_callback=__on_confirmation_result, action_name=f"Remove a `{self.__public_key.alias}` key alias."
            )
        )


class KeyAliasesHeader(ColumnLayout):
    def compose(self) -> ComposeResult:
        yield StaticColumn("No.", id="key-alias-row-number", classes=even)
        yield StaticColumn("Alias", id="key-alias-name", classes=odd)
        yield StaticColumn("Public key", id="key-alias-public-key", classes=even)
        yield StaticColumn("Actions", id="actions", classes=odd)


class ManageKeyAliases(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
        Binding("f2", "new_key_alias", "New alias"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.__scrollable_part = ScrollablePart()

    def create_main_panel(self) -> ComposeResult:
        yield BigTitle("key aliases")
        yield KeyAliasesHeader()
        with self.__scrollable_part:
            for idx, key in enumerate(self.app.world.profile_data.working_account.keys):
                yield KeyAlias(idx, key)

    def action_new_key_alias(self) -> None:
        self.app.push_screen(NewKeyAlias())

    @on(KeyAlias.Changed)
    @on(KeyAliasForm.Changed)
    def rebuild_key_aliases(self) -> None:
        self.query(KeyAlias).remove()

        for idx, key in enumerate(self.app.world.profile_data.working_account.keys):
            self.__scrollable_part.mount(KeyAlias(idx, key))
