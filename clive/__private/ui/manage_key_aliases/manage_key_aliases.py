from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Static

from clive.__private.ui.confirm_with_password.confirm_with_password import ConfirmWithPassword
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.manage_key_aliases.edit_key_alias import EditKeyAlias
from clive.__private.ui.manage_key_aliases.new_key_alias import NewKeyAlias
from clive.__private.ui.manage_key_aliases.widgets.key_alias_form import KeyAliasForm
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_checkerboard_table import (
    EVEN_CLASS_NAME,
    ODD_CLASS_NAME,
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.clive_screen import CliveScreen
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section_title import SectionTitle

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.keys import PublicKeyAliased


class KeyAlias(CliveCheckerboardTableRow, CliveWidget):
    """Row of ManageKeyAliasesTable."""

    class Changed(Message):
        """Emitted when key alias have been changed."""

    def __init__(self, index: int, public_key: PublicKeyAliased) -> None:
        self.__public_key = public_key

        super().__init__(
            CliveCheckerBoardTableCell(str(index + 1)),
            CliveCheckerBoardTableCell(self.__public_key.alias),
            CliveCheckerBoardTableCell(self.__public_key.value, classes="public-key"),
            CliveCheckerBoardTableCell(
                Horizontal(
                    CliveButton("Edit", id_="edit-key-alias-button"),
                    CliveButton("Remove", variant="error", id_="remove-key-alias-button"),
                ),
            ),
        )

    @on(CliveButton.Pressed, "#edit-key-alias-button")
    def push_edit_key_alias_screen(self) -> None:
        self.app.push_screen(EditKeyAlias(self.__public_key))

    @on(CliveButton.Pressed, "#remove-key-alias-button")
    async def remove_key_alias(self) -> None:
        @CliveScreen.try_again_after_activation
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


class KeyAliasesHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("No.", classes=ODD_CLASS_NAME)
        yield Static("Alias", classes=EVEN_CLASS_NAME)
        yield Static("Public key", classes=f"{ODD_CLASS_NAME} public-key")
        yield Static("Actions", classes=EVEN_CLASS_NAME)


class ManageKeyAliasesTable(CliveCheckerboardTable):
    """Table with KeyAliases."""

    def create_static_rows(self) -> list[KeyAlias]:
        key_aliases = []
        for idx, key in enumerate(self.app.world.profile_data.working_account.keys):
            key_aliases.append(KeyAlias(idx, key))

        return key_aliases


class ManageKeyAliases(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
        Binding("f2", "new_key_alias", "New alias"),
    ]

    BIG_TITLE = "configuration"
    SUBTITLE = "Manage key aliases"

    def __init__(self) -> None:
        super().__init__()
        self.__scrollable_part = ScrollablePart()

    def create_main_panel(self) -> ComposeResult:
        with self.__scrollable_part:
            yield ManageKeyAliasesTable(SectionTitle("Edit key aliases"), KeyAliasesHeader())

    def action_new_key_alias(self) -> None:
        self.app.push_screen(NewKeyAlias())

    @on(KeyAlias.Changed)
    @on(KeyAliasForm.Changed)
    async def rebuild_key_aliases(self) -> None:
        await self.query_one(ManageKeyAliasesTable).rebuild()
