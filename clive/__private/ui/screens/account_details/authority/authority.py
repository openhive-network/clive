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
    CliveAuthorityEntryAccountRegular,
    CliveAuthorityEntryKeyBase,
    CliveAuthorityEntryKeyRegular,
    CliveAuthorityEntryMemo,
    CliveAuthorityRoleMemo,
    CliveAuthorityRoleRegular,
    CliveAuthorityWeightedEntryBase,
)
from clive.__private.core.constants.tui.class_names import CLIVE_EVEN_COLUMN_CLASS_NAME, CLIVE_ODD_COLUMN_CLASS_NAME
from clive.__private.core.keys import PublicKey
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

    def __init__(self, key_alias: str) -> None:
        super().__init__("Remove", "error")
        self._key_alias = key_alias

    @on(Pressed)
    def remove_private_key(self) -> None:
        self.app.push_screen(RemoveKeyAliasDialog(key_alias=self._key_alias), self._key_aliases_changed_callback)


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
            for authority_type in self.query(AuthorityRole):
                authority_type.update(*filter_patterns)

        if self.operation.account not in selected_accounts_in_filter:
            self.display = False
            return False

        if not filter_patterns:
            self.display = True
            update_display_of_authority_types()
            return True

        for role in self.operation.roles:
            if role.is_matching_pattern(*filter_patterns):
                self.display = True
                update_display_of_authority_types()
                return True
        self.display = False
        return False

    def _create_widgets_to_mount(self, *, collapsed: bool) -> list[AuthorityRole]:
        widgets_to_mount = []

        for role in self._operation.roles:
            is_role_memo = isinstance(role, CliveAuthorityRoleMemo)
            title = "memo key" if is_role_memo else role.level
            widgets_to_mount.append(AuthorityRole(role, title=title, collapsed=collapsed))

        return widgets_to_mount


class AuthorityRole(CliveCollapsible):
    def __init__(
        self,
        authority_role: CliveAuthorityRoleRegular | CliveAuthorityRoleMemo,
        *,
        title: str,
        collapsed: bool = False,
    ) -> None:
        self._authority_role = authority_role
        super().__init__(
            AuthorityTable(authority_role),
            title=title,
            collapsed=collapsed,
            right_hand_side_text=self._get_right_hand_side_text(),
        )

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

        if not self._authority_role:
            self.display = False
            return

        matched = self._authority_role.is_matching_pattern(*filter_patterns)
        self.display = matched

        if matched:
            update_display_in_authority_table()

    def _get_right_hand_side_text(self) -> str | None:
        authority_role = self._authority_role
        if isinstance(authority_role, CliveAuthorityRoleMemo):
            return None

        weight_threshold = authority_role.weight_threshold
        imported_weights = authority_role.sum_weights_of_already_imported_keys(self.profile.keys)
        return f"imported weights: {imported_weights}, threshold: {weight_threshold}"


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

    def __init__(
        self, entry: CliveAuthorityEntryKeyRegular | CliveAuthorityEntryAccountRegular | CliveAuthorityEntryMemo
    ) -> None:
        self._entry = entry
        self._is_account_entry = isinstance(entry, CliveAuthorityEntryAccountRegular)
        self._is_weighted_entry = isinstance(entry, CliveAuthorityWeightedEntryBase)
        super().__init__(*self._create_cells())

    @property
    def ensure_key_based_entry(self) -> CliveAuthorityEntryKeyBase:
        assert isinstance(self._entry, CliveAuthorityEntryKeyBase), "Invalid type of entry."
        return self._entry

    @property
    def ensure_weighted_entry(self) -> CliveAuthorityWeightedEntryBase:
        assert isinstance(self._entry, CliveAuthorityWeightedEntryBase), "Invalid type of entry."
        return self._entry

    @property
    def entry_value(self) -> str:
        return self._entry.value

    @property
    def alias(self) -> str | None:
        alias: str | None = None
        if not self._is_account_entry and self.entry_value in self.profile.keys:
            alias = self.profile.keys.get_first_from_public_key(self.entry_value).alias
        return alias

    def update(self, *filter_patterns: str) -> None:
        """
        Update the display based on filter patterns.

        Args:
            *filter_patterns: Patterns to filter the entries in the authority.
        """
        filter_pattern_present = bool(filter_patterns)
        self.display = self._entry.is_matching_pattern(*filter_patterns) if filter_pattern_present else True

    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        key_or_account_text = self._generate_key_or_account_text()

        action_widget: Widget | None

        if self._is_account_entry:
            # we can't add corresponding key to the account, so we just display static widget without text
            action_widget = Static()
        else:
            alias = self.alias
            action_widget = (
                RemovePrivateKeyButton(alias)
                if alias
                else ImportPrivateKeyButton(public_key=self.ensure_key_based_entry.public_key)
            )

        cells = [
            (
                CliveCheckerBoardTableCell(
                    key_or_account_text, classes="key-or-account" if self._is_weighted_entry else "memo-key"
                )
            )
        ]
        if self._is_weighted_entry:
            cells.append(CliveCheckerBoardTableCell(str(self.ensure_weighted_entry.weight), classes="weight"))
        cells.append(CliveCheckerBoardTableCell(action_widget, classes="action"))
        return cells

    def _generate_key_or_account_text(self) -> str:
        """
        Generate the text for the key or account cell.

        Returns:
            The text to be displayed in the key or account cell.
        """
        entry_value = self.entry_value
        if self._is_account_entry:
            return entry_value

        alias = self.alias
        if alias in (None, entry_value):
            return entry_value
        return f"{alias} ({entry_value})"


class AuthorityTable(CliveCheckerboardTable):
    """
    A table containing all entries of a single type of authority.

    Attributes:
        NO_CONTENT_TEXT: Text displayed when there are no entries in the authority.

    Args:
        authority_role: Object representing authority role.
    """

    NO_CONTENT_TEXT = "No entries in authority"

    def __init__(self, authority_role: CliveAuthorityRoleRegular | CliveAuthorityRoleMemo) -> None:
        self._authority_role = authority_role
        is_role_memo = isinstance(authority_role, CliveAuthorityRoleMemo)
        super().__init__(header=AuthorityHeader(memo_header=is_role_memo))

    def create_static_rows(self) -> Sequence[AuthorityItem]:
        return [AuthorityItem(entry) for entry in self._authority_role.get_entries()]

    def update_cell_colors(self) -> None:
        """Update background colors according to the actual displayed rows."""
        displayed_rows = [row for row in self.query(CliveCheckerboardTableRow) if row.display]

        for row_index, row in enumerate(displayed_rows):
            for cell_index, cell in enumerate(row.cells):
                should_be_even = (row_index + cell_index) % 2 == 0

                if should_be_even:
                    cell.remove_class(CLIVE_ODD_COLUMN_CLASS_NAME)
                    cell.add_class(CLIVE_EVEN_COLUMN_CLASS_NAME)
                else:
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
            all_patterns.extend(
                [key.value for key in self.profile.keys.get_key_values_by_alias_pattern(filter_pattern)]
            )
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
                suggestions_to_add = [entry.value for entry in operation.get_entries()]
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
