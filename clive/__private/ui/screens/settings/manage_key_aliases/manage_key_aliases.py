from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal, HorizontalGroup, Right
from textual.events import Mount
from textual.widgets import Static

from clive.__private.core.constants.tui.class_names import CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME
from clive.__private.core.constants.tui.texts import LOADING_TEXT
from clive.__private.ui.bindings import CLIVE_PREDEFINED_BINDINGS
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.dialogs import EditKeyAliasDialog, NewKeyAliasDialog, RemoveKeyAliasDialog
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.not_updated_yet import NotUpdatedYet
from clive.__private.ui.screens.base_screen import BaseScreen
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


class AddNewKeyAliasButton(CliveButton):
    DEFAULT_CSS = """
    AddNewKeyAliasButton {
        width: 22;
    }
    """

    class Pressed(CliveButton.Pressed):
        """Message sent when AddNewKeyAliasButton is pressed."""

    def __init__(self) -> None:
        super().__init__(
            "Add new alias",
            binding=self.custom_bindings.manage_key_aliases.add_new_alias,
            variant="success",
        )


class ButtonContainer(HorizontalGroup):
    def compose(self) -> ComposeResult:
        with Right():
            yield AddNewKeyAliasButton()


class EditKeyAliasButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Message sent when EditKeyAliasButton is pressed."""

    def __init__(self) -> None:
        super().__init__("Edit", id_="edit-key-alias-button")


class RemoveKeyAliasButton(CliveButton):
    class Pressed(CliveButton.Pressed):
        """Message sent when RemoveKeyAliasButton is pressed."""

    def __init__(self) -> None:
        super().__init__("Remove", variant="error", id_="remove-key-alias-button")


class KeyAliasRow(CliveCheckerboardTableRow, CliveWidget):
    """
    Row of ManageKeyAliasesTable.

    Args:
        public_key: Aliased public key that row represents.
    """

    def __init__(self, public_key: PublicKeyAliased) -> None:
        self._public_key = public_key
        super().__init__(*self._create_cells())

    @property
    def index_cell(self) -> CliveCheckerBoardTableCell:
        return self.query_exactly_one("#index-cell", CliveCheckerBoardTableCell)

    @on(Mount)
    async def update_index_cell(self) -> None:
        """
        Update content of index cell.

        The index cell is initialized with a LOADING_TEXT because of the row index,
        which is assigned automatically later, during row creation. The cell content is
        updated here once the row is fully created and its index becomes available.
        """
        await self.index_cell.update_content(self.humanize_row_number())

    @on(EditKeyAliasButton.Pressed)
    def push_edit_key_alias_dialog(self) -> None:
        self.app.push_screen(EditKeyAliasDialog(self._public_key))

    @on(RemoveKeyAliasButton.Pressed)
    def remove_key_alias(self) -> None:
        self.app.push_screen(RemoveKeyAliasDialog(self._public_key.alias))

    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        return [
            CliveCheckerBoardTableCell(LOADING_TEXT, id_="index-cell"),
            CliveCheckerBoardTableCell(self._public_key.alias),
            CliveCheckerBoardTableCell(self._public_key.value, classes="public-key"),
            CliveCheckerBoardTableCell(
                Horizontal(
                    EditKeyAliasButton(),
                    RemoveKeyAliasButton(),
                ),
            ),
        ]


class KeyAliasesHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("No.", classes=CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME)
        yield Static("Alias", classes=CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME)
        yield Static("Public key", classes=f"{CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME} public-key")
        yield Static("Actions", classes=CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME)


class ManageKeyAliasesTable(CliveCheckerboardTable):
    """Table with KeyAliases."""

    ATTRIBUTE_TO_WATCH = "profile_reactive"
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
        return [KeyAliasRow(key) for key in content.keys]

    def check_if_should_be_updated(self, content: Profile) -> bool:
        actual_key_aliases = list(content.keys)
        return actual_key_aliases != self._previous_key_aliases

    def update_previous_state(self, content: Profile) -> None:
        self._previous_key_aliases = list(content.keys)


class ManageKeyAliases(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        CLIVE_PREDEFINED_BINDINGS.manage_key_aliases.add_new_alias.create(show=False),
    ]

    BIG_TITLE = "Settings"
    SUBTITLE = "Manage key aliases"

    def __init__(self) -> None:
        super().__init__()
        self.__scrollable_part = ScrollablePart()

    def create_main_panel(self) -> ComposeResult:
        yield ButtonContainer()
        with self.__scrollable_part:
            yield ManageKeyAliasesTable()

    @on(AddNewKeyAliasButton.Pressed)
    def action_add_new_alias(self) -> None:
        self.app.push_screen(NewKeyAliasDialog())
