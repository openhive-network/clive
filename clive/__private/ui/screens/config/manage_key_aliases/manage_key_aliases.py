from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Static

from clive.__private.core.constants.tui.class_names import CLIVE_EVEN_COLUMN_CLASS_NAME, CLIVE_ODD_COLUMN_CLASS_NAME
from clive.__private.ui.clive_screen import CliveScreen
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.not_updated_yet import NotUpdatedYet
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.screens.config.manage_key_aliases.edit_key_alias import EditKeyAlias
from clive.__private.ui.screens.config.manage_key_aliases.new_key_alias import NewKeyAlias
from clive.__private.ui.screens.confirm_with_password.confirm_with_password import ConfirmWithPassword
from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.clive_basic import (
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.scrolling import ScrollablePart

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.keys import PublicKeyAliased
    from clive.__private.core.profile import Profile
    from clive.__private.core.world import TUIWorld


class KeyAliasRow(CliveCheckerboardTableRow, CliveWidget):
    """Row of ManageKeyAliasesTable."""

    def __init__(self, index: int, public_key: PublicKeyAliased) -> None:
        self._index = index
        self._public_key = public_key
        super().__init__(*self._create_cells())

    @on(CliveButton.Pressed, "#edit-key-alias-button")
    def push_edit_key_alias_screen(self) -> None:
        self.app.push_screen(EditKeyAlias(self._public_key))

    @on(CliveButton.Pressed, "#remove-key-alias-button")
    def remove_key_alias(self) -> None:
        @CliveScreen.try_again_after_unlock
        async def _remove_key_alias(password: str | None) -> None:
            if not password:
                return

            self.profile.keys.remove(self._public_key)
            self.notify(f"Key alias `{self._public_key.alias}` was removed.")
            self.app.trigger_profile_watchers()

        self.app.push_screen(
            ConfirmWithPassword(title=f"Remove a `{self._public_key.alias}` key alias."),
            _remove_key_alias,
        )

    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        return [
            CliveCheckerBoardTableCell(str(self._index + 1)),
            CliveCheckerBoardTableCell(self._public_key.alias),
            CliveCheckerBoardTableCell(self._public_key.value, classes="public-key"),
            CliveCheckerBoardTableCell(
                Horizontal(
                    CliveButton("Edit", id_="edit-key-alias-button"),
                    CliveButton("Remove", variant="error", id_="remove-key-alias-button"),
                ),
            ),
        ]


class KeyAliasesHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("No.", classes=CLIVE_ODD_COLUMN_CLASS_NAME)
        yield Static("Alias", classes=CLIVE_EVEN_COLUMN_CLASS_NAME)
        yield Static("Public key", classes=f"{CLIVE_ODD_COLUMN_CLASS_NAME} public-key")
        yield Static("Actions", classes=CLIVE_EVEN_COLUMN_CLASS_NAME)


class ManageKeyAliasesTable(CliveCheckerboardTable):
    """Table with KeyAliases."""

    ATTRIBUTE_TO_WATCH = "profile"
    NO_CONTENT_TEXT = "You have no key aliases"

    def __init__(self) -> None:
        super().__init__(header=KeyAliasesHeader(), title="Edit key aliases")
        self._previous_key_aliases: list[PublicKeyAliased] | NotUpdatedYet = NotUpdatedYet()

    @property
    def object_to_watch(self) -> TUIWorld:
        return self.world

    def is_anything_to_display(self, content: Profile) -> bool:
        return bool(content.keys)

    def create_dynamic_rows(self, content: Profile) -> list[KeyAliasRow]:
        return [KeyAliasRow(index, key) for index, key in enumerate(content.keys)]

    def check_if_should_be_updated(self, content: Profile) -> bool:
        actual_key_aliases = list(content.keys)
        return actual_key_aliases != self._previous_key_aliases

    def update_previous_state(self, content: Profile) -> None:
        self._previous_key_aliases = list(content.keys)


class ManageKeyAliases(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("f2", "new_key_alias", "New alias"),
    ]

    BIG_TITLE = "configuration"
    SUBTITLE = "Manage key aliases"

    def __init__(self) -> None:
        super().__init__()
        self.__scrollable_part = ScrollablePart()

    def create_main_panel(self) -> ComposeResult:
        with self.__scrollable_part:
            yield ManageKeyAliasesTable()

    def action_new_key_alias(self) -> None:
        self.app.push_screen(NewKeyAlias())
