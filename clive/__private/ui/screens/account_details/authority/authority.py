from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual import on
from textual.containers import Container, Horizontal
from textual.css.query import NoMatches
from textual.message import Message
from textual.widgets import Static, TabPane
from textual.widgets._collapsible import CollapsibleTitle

from clive.__private.core.clive_authority import (
    CliveAuthority,
    CliveAuthorityEntryWrapper,
    CliveAuthorityWrapper,
)
from clive.__private.core.constants.tui.class_names import CLIVE_EVEN_COLUMN_CLASS_NAME, CLIVE_ODD_COLUMN_CLASS_NAME
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.dialogs import NewKeyAliasDialog, RemoveKeyAliasDialog
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.screens.account_details.authority.filter_authority import FilterAuthority
from clive.__private.ui.widgets.buttons import (
    CliveButton,
    OneLineButton,
)
from clive.__private.ui.widgets.clive_basic import (
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
    CliveCollapsible,
)
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from clive.__private.ui.widgets.section import SectionBody, SectionScrollable
from wax.complex_operations.account_update import AccountAuthorityUpdateOperation

if TYPE_CHECKING:
    from collections.abc import Sequence

    from rich.text import TextType
    from textual.app import ComposeResult
    from textual.widget import Widget

    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.keys import PublicKey
    from clive.__private.ui.widgets.buttons.clive_button import CliveButtonVariant


class PrivateKeyActionButton(OneLineButton):
    class KeyAliasesChanged(Message):
        """Message sent when key aliases in KeyManager were modified."""

    def __init__(self, label: TextType, variant: CliveButtonVariant) -> None:
        super().__init__(label, variant)

    def _key_aliases_changed_callback(self, confirm: bool | None) -> None:  # noqa: FBT001
        if confirm:
            self.post_message(self.KeyAliasesChanged())


class ImportPrivateKeyButton(PrivateKeyActionButton):
    class Pressed(PrivateKeyActionButton.Pressed):
        """Message sent when ImportPrivateKeyButton is pressed."""

    def __init__(self, public_key: PublicKey) -> None:
        super().__init__("Import key", "success")
        self._public_key = public_key

    @on(Pressed)
    def add_private_key(self) -> None:
        self.app.push_screen(
            NewKeyAliasDialog(public_key_to_match=self._public_key), self._key_aliases_changed_callback
        )


class RemovePrivateKeyButton(PrivateKeyActionButton):
    class Pressed(PrivateKeyActionButton.Pressed):
        """Message sent when RemovePrivateKeyButton is pressed."""

    def __init__(self, *key_aliases: str) -> None:
        super().__init__("Remove", "error")
        self._key_aliases = key_aliases

    @on(Pressed)
    def remove_private_key(self) -> None:
        self.app.push_screen(RemoveKeyAliasDialog(*self._key_aliases), self._key_aliases_changed_callback)


class AuthorityRoles(SectionScrollable):
    """Widget for storing all AccountCollapsibles."""

    def __init__(self) -> None:
        super().__init__("Authority roles")

    @property
    def body(self) -> SectionBody:
        return self.query_exactly_one(SectionBody)

    async def build(self, authority_operations: list[CliveAuthority]) -> None:
        await self.body.mount_all([AccountCollapsible(operation) for operation in authority_operations])

    async def rebuild(self, authority_operations: list[CliveAuthority]) -> None:
        await self.body.query("*").remove()
        await self.build(authority_operations)

    async def update(self, selected_accounts_in_filter: list[str], *filter_patterns: str) -> None:
        """
        Update the display of AuthorityRoles based on filter patterns selected accounts in filter.

        This method updates each AccountCollapsible inside the body of AuthorityRoles. Also handles NoContentAvailable
        widget.

        Args:
            selected_accounts_in_filter: Accounts selected in the filter.
            *filter_patterns: Patterns to filter the entries in the authority.
        """
        results = [
            account_collapsible.update(selected_accounts_in_filter, *filter_patterns)
            for account_collapsible in self.body.query(AccountCollapsible)
        ]
        if any(results):
            await self._remove_no_content_available_widget()
        else:
            try:
                self.body.query_exactly_one(NoContentAvailable)
            except NoMatches:
                self._mount_no_content_available_widget()

    def _mount_no_content_available_widget(self) -> None:
        self.body.mount(NoContentAvailable("There are no authorities that match filter criteria."))

    async def _remove_no_content_available_widget(self) -> None:
        await self.body.query(NoContentAvailable).remove()


class AccountCollapsible(CliveCollapsible):
    def __init__(
        self,
        operation: CliveAuthority,
        *,
        collapsed: bool = False,
    ) -> None:
        self._operation = operation
        super().__init__(
            *self._create_widgets_to_mount(collapsed=collapsed),
            title=operation.account,
            collapsed=collapsed,
        )

    @property
    def operation(self) -> CliveAuthority:
        return self._operation

    def update(self, selected_accounts_in_filter: list[str], *filter_patterns: str) -> bool:
        """
        Update the display of AccountCollapsible based on accounts selected in filter and filter patterns.

        Args:
            selected_accounts_in_filter: Accounts selected in the filter.
            *filter_patterns: Patterns to filter the entries in the authority.

        Returns:
            True if the display of widget is enabled, False otherwise.
        """

        def update_display_of_authority_types() -> None:
            """Update the display of AuthorityType widgets within this AccountCollapsible."""
            for authority_type in self.query(AuthorityType):
                authority_type.update(*filter_patterns)

        if self.operation.account not in selected_accounts_in_filter:
            self.display = False
            return False

        if not filter_patterns:
            self.display = True
            update_display_of_authority_types()
            return True

        for role in self.operation.roles:
            if role.is_role_has_entry_that_matches_pattern(*filter_patterns):
                self.display = True
                update_display_of_authority_types()
                return True
        self.display = False
        return False

    def _create_widgets_to_mount(self, *, collapsed: bool) -> list[AuthorityType]:
        widgets_to_mount = []

        for role in self._operation.roles:
            title = role.level if not role.is_role_memo else "memo key"
            widgets_to_mount.append(AuthorityType(role.value, title=title, collapsed=collapsed))

        return widgets_to_mount


class AuthorityType(CliveCollapsible):
    def __init__(
        self,
        account_authorities: CliveAuthorityEntryWrapper | CliveAuthorityWrapper | None,
        *,
        title: str,
        collapsed: bool = False,
    ) -> None:
        self._account_authorities = account_authorities
        super().__init__(
            AuthorityTable(account_authorities),
            title=title,
            collapsed=collapsed,
            right_hand_side_text=self._get_right_hand_side_text(),
        )

    @property
    def authority(self) -> CliveAuthorityEntryWrapper | CliveAuthorityWrapper | None:
        return self._account_authorities

    def update(self, *filter_patterns: str) -> None:
        """
        Update the display of AuthorityType based on filter patterns.

        Args:
            *filter_patterns: Patterns to filter the entries in the authority.
        """

        def update_display_in_authority_table() -> None:
            authority_table = self.query_exactly_one(AuthorityTable)
            authority_table.update(*filter_patterns)

        filter_pattern_present = bool(filter_patterns)
        if not filter_pattern_present:
            self.display = True
            update_display_in_authority_table()
            return

        if not self._account_authorities:
            self.display = False
            return

        matched = self._account_authorities.is_match(*filter_patterns)
        self.display = matched

        if matched:
            update_display_in_authority_table()

    def _get_right_hand_side_text(self) -> str | None:
        right_hand_side_text = None

        if self._account_authorities and isinstance(self._account_authorities, CliveAuthorityWrapper):
            weight_threshold = self._account_authorities.weight_threshold
            collected_weights = self._account_authorities.collect_weights(self.profile.keys)
            right_hand_side_text = f"imported weights: {sum(collected_weights)}, threshold: {weight_threshold}"

        return right_hand_side_text


class AuthorityHeader(Horizontal):
    def __init__(self, *, memo_header: bool = False) -> None:
        super().__init__()
        self._memo_header = memo_header

    def compose(self) -> ComposeResult:
        if not self._memo_header:
            yield Static("Key / Account", classes=f"{CLIVE_ODD_COLUMN_CLASS_NAME} key-or-account")
            yield Static("Weight", classes=f"{CLIVE_EVEN_COLUMN_CLASS_NAME} weight")
            yield Static("Wallet keys", classes=f"{CLIVE_ODD_COLUMN_CLASS_NAME} action")
        else:
            yield Static("Key", classes=f"{CLIVE_ODD_COLUMN_CLASS_NAME} memo-key")
            yield Static("Wallet keys", classes=f"{CLIVE_EVEN_COLUMN_CLASS_NAME} action")


class AuthorityItem(CliveCheckerboardTableRow):
    """
    Class for items in the  authority table.

    Args:
        entry: Object representing the authority entry.
    """

    def __init__(self, entry: CliveAuthorityEntryWrapper) -> None:
        self._entry = entry
        self._weight = entry.weight
        self._is_account_entry = entry.is_account_entry
        super().__init__(*self._create_cells())

    @property
    def aliases(self) -> list[str]:
        aliases: list[str] = []
        if not self._is_account_entry and self.entry in self.profile.keys:
            aliases = [aliased_key.alias for aliased_key in self.profile.keys.get_all_from_public_key(self.entry)]
        return aliases

    @property
    def entry(self) -> str:
        return self._entry.key_or_account

    def update(self, *filter_patterns: str) -> None:
        """
        Update the display based on filter patterns.

        Args:
            *filter_patterns: Patterns to filter the entries in the authority.
        """
        filter_pattern_present = bool(filter_patterns)
        self.display = self._entry.is_match(*filter_patterns) if filter_pattern_present else True

    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        key_or_account_text = self._generate_key_or_account_text()

        action_widget: Widget | None = None

        if self._is_account_entry:
            # we can't add corresponding key to the account, so we just display static widget without text
            action_widget = Static()
        else:
            aliases = self.aliases
            action_widget = (
                RemovePrivateKeyButton(*aliases)
                if aliases
                else ImportPrivateKeyButton(public_key=self._entry.public_key)
            )

        cells = [
            (CliveCheckerBoardTableCell(key_or_account_text, classes="key-or-account" if self._weight else "memo-key"))
        ]
        if self._weight:
            cells.append(CliveCheckerBoardTableCell(str(self._weight), classes="weight"))
        cells.append(CliveCheckerBoardTableCell(action_widget, classes="action"))
        return cells

    def _generate_key_or_account_text(self) -> str:
        """
        Generate the text for the key or account cell.

        Returns:
            The text to be displayed in the key or account cell.
        """
        key_or_account_text = self._entry.key_or_account

        if not self._is_account_entry and self._entry.key_or_account in self.profile.keys:
            aliases = self.aliases
            if len(aliases) == 1:
                alias = next(iter(aliases))
                if alias != self._entry.key_or_account:
                    key_or_account_text = f"{alias} ({self._entry.key_or_account})"
            else:
                key_or_account_text = f"many aliases ({self._entry.key_or_account})"

        return key_or_account_text


class AuthorityTable(CliveCheckerboardTable):
    """
    A table containing all entries of a single type of authority.

    Attributes:
        NO_CONTENT_TEXT: Text displayed when there are no entries in the authority.

    Args:
        single_authority: Object representing single authority.
    """

    NO_CONTENT_TEXT = "No entries in authority"

    def __init__(self, single_authority: CliveAuthorityEntryWrapper | CliveAuthorityWrapper | None) -> None:
        self._single_authority = single_authority
        is_memo_authority = False
        if single_authority:
            is_memo_authority = single_authority.is_memo_authority
        super().__init__(header=AuthorityHeader(memo_header=is_memo_authority))

    def create_static_rows(self) -> Sequence[AuthorityItem]:
        if not self._single_authority:  # no entries in this type of authority
            return []

        return [AuthorityItem(wrapper_object) for wrapper_object in self._single_authority.get()]

    def update_cell_colors(self) -> None:
        """Update background colors according to the actual displayed rows."""
        displayed_rows = [row for row in self.query(CliveCheckerboardTableRow) if row.display]
        for row_index, row in enumerate(displayed_rows):
            is_row_even = row_index % 2 == 0
            for cell_index, cell in enumerate(row.cells):
                is_cell_even = cell_index % 2 == 0
                if (is_row_even and is_cell_even) or (
                    (not is_row_even and not is_cell_even) and cell.has_class(CLIVE_ODD_COLUMN_CLASS_NAME)
                ):
                    cell.remove_class(CLIVE_ODD_COLUMN_CLASS_NAME)
                    cell.add_class(CLIVE_EVEN_COLUMN_CLASS_NAME)

                elif (not is_row_even and is_cell_even) or (
                    (is_row_even and not is_cell_even) and cell.has_class(CLIVE_EVEN_COLUMN_CLASS_NAME)
                ):
                    cell.remove_class(CLIVE_EVEN_COLUMN_CLASS_NAME)
                    cell.add_class(CLIVE_ODD_COLUMN_CLASS_NAME)

    def update(self, *filter_patterns: str) -> None:
        for row in self.query(CliveCheckerboardTableRow):
            assert isinstance(row, (AuthorityItem)), "Invalid type of row."
            row.update(*filter_patterns)
            self.update_cell_colors()


class Authority(TabPane, CliveWidget):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    AUTHORITY_TAB_PANE_TITLE: Final[str] = "Authority"

    def __init__(self, account: TrackedAccount) -> None:
        super().__init__(self.AUTHORITY_TAB_PANE_TITLE)
        self._account = account
        self._authority_operations: list[CliveAuthority] = []
        self._filter_pattern_already_applied: bool = False

    async def on_mount(self) -> None:
        await self._collect_authorities()
        self._update_input_suggestions()
        await self.authority_roles.build(self._authority_operations)
        await self._update_display_inside_authority_roles()

    def compose(self) -> ComposeResult:
        with Horizontal(id="filter-and-modify"):
            yield FilterAuthority(self._account)
            yield Container(
                CliveButton(label="Modify", variant="success", id_="modify-button", disabled=True),
                id="button-container",
            )
        yield AuthorityRoles()

    @property
    def authority_roles(self) -> AuthorityRoles:
        return self.query_exactly_one(AuthorityRoles)

    @property
    def filter_authority(self) -> FilterAuthority:
        return self.query_exactly_one(FilterAuthority)

    @on(FilterAuthority.AuthorityFilterReady)
    async def _apply_authority_filter(self) -> None:
        """Apply the authority filter based on the input and update the UI."""
        authority_filter_input = self.filter_authority.authority_filter_input
        filter_pattern = authority_filter_input.value_or_error
        all_patterns = []

        if filter_pattern:
            self._update_input_suggestions()
            all_patterns.extend(self.profile.keys.get_key_values_by_alias_pattern(filter_pattern))
            all_patterns.append(filter_pattern)

        self.filter_authority.collapse_account_filter_collapsible()
        await self._update_display_inside_authority_roles(*all_patterns)

    @on(PrivateKeyActionButton.KeyAliasesChanged)
    async def rebuild_after_key_aliases_changed(self) -> None:
        await self._rebuild_authority_roles()
        await self._apply_authority_filter()

    @on(FilterAuthority.Cleared)
    async def handle_filter_cleared(self) -> None:
        self._update_input_suggestions()
        await self._update_display_inside_authority_roles()

    @on(FilterAuthority.SelectedAccountsChanged)
    def _update_authorities_and_suggestions_after_account_in_filter_changed(self) -> None:
        self._update_input_suggestions()

    async def _collect_authorities(self) -> None:
        tracked_accounts = self.profile.accounts.tracked

        for account in tracked_accounts:
            authority_operation = await AccountAuthorityUpdateOperation.create_for(
                self.world.wax_interface, account.name
            )
            self._authority_operations.append(CliveAuthority(authority_operation))

    async def _update_display_inside_authority_roles(self, *filter_patterns: str) -> None:
        with self.app.batch_update():
            await self.authority_roles.update(self.filter_authority.selected_options, *filter_patterns)

    def _update_input_suggestions(self) -> None:
        input_suggestions: set[str] = set()
        filter_authority = self.filter_authority

        options_selected_in_filter = filter_authority.selected_options
        for operation in self._authority_operations:
            if operation.account in options_selected_in_filter:
                suggestions_to_add = [wrapper_object.key_or_account for wrapper_object in operation.get()]
                input_suggestions.update(suggestions_to_add)

        input_suggestions.update(self.profile.keys.get_all_aliases())
        filter_authority.authority_filter_input.clear_suggestions()
        filter_authority.authority_filter_input.add_suggestion(*input_suggestions)

    async def _rebuild_authority_roles(self) -> None:
        with self.app.batch_update():
            await self.authority_roles.rebuild(self._authority_operations)

            # somehow after mounting widgets inside authority roles body scroll is moved down, so focus first mounted
            # account collapsible title (and move the scroll by it) then refocus previously focused widget.
            previously_focused = self.app.focused
            all_account_collapsible_titles = self.query(CollapsibleTitle)
            if all_account_collapsible_titles:
                all_account_collapsible_titles.first().focus()
                if previously_focused:
                    previously_focused.focus()
