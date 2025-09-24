from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Final

from textual import on
from textual.containers import Container, Horizontal
from textual.css.query import NoMatches
from textual.message import Message
from textual.widgets import Static, TabPane
from textual.widgets._collapsible import CollapsibleTitle

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
from clive.__private.ui.widgets.no_filter_criteria_match import NoFilterCriteriaMatch
from clive.__private.ui.widgets.section import SectionBody, SectionScrollable

if TYPE_CHECKING:
    from collections.abc import Sequence

    from rich.text import TextType
    from textual.app import ComposeResult
    from textual.css.query import DOMQuery
    from textual.widget import Widget

    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.authority import (
        Authority,
        AuthorityEntryAccountRegular,
        AuthorityEntryKeyRegular,
        AuthorityEntryMemo,
        AuthorityRoleMemo,
        AuthorityRoleRegular,
    )
    from clive.__private.core.keys import PublicKey
    from clive.__private.core.keys.keys import PublicKeyAliased
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


class RemoveKeyAliasButton(PrivateKeyActionButton):
    class Pressed(PrivateKeyActionButton.Pressed):
        """Message sent when RemoveKeyAliasButton is pressed."""

    def __init__(self, *keys_to_remove: PublicKeyAliased) -> None:
        super().__init__("Remove", "error")
        self._keys_to_remove = keys_to_remove

    @on(Pressed)
    def remove_private_key(self) -> None:
        self.app.push_screen(RemoveKeyAliasDialog(*self._keys_to_remove), self._key_aliases_changed_callback)


class AccountsAuthorities(SectionScrollable):
    """
    Widget for storing all AccountCollapsibles.

    Args:
        initial_account: The account that is initially selected in the filter.
    """

    def __init__(self, initial_account: TrackedAccount) -> None:
        super().__init__("Authority roles")
        self._initial_account = initial_account

    @property
    def body(self) -> SectionBody:
        return self.query_exactly_one(SectionBody)

    @property
    def account_collapsibles(self) -> DOMQuery[AccountCollapsible]:
        return self.body.query(AccountCollapsible)

    async def build(self, authorities: list[Authority]) -> None:
        await self.body.mount_all([AccountCollapsible(authority) for authority in authorities])

    async def rebuild(self, authorities: list[Authority]) -> None:
        with self.app.batch_update():
            await self.body.query("*").remove()
            await self.build(authorities)

    def filter(self, selected_accounts_in_filter: list[str], *filter_patterns: str) -> None:
        """
        Update the display based on filter patterns and selected accounts in filter.

        This method updates each collapsible representing account inside the body of this widget. Also handles
        NoFilterCriteriaMatch widget.

        Args:
            selected_accounts_in_filter: Accounts selected in the filter.
            *filter_patterns: Patterns to filter the entries in the authority.
        """
        account_collapsibles = list(self.account_collapsibles)

        for account_collapsible in account_collapsibles:
            account_collapsible.filter(selected_accounts_in_filter, *filter_patterns)

        is_any_account_collapsible_displayed = any(collapsible.display for collapsible in account_collapsibles)
        if is_any_account_collapsible_displayed:
            self._remove_no_filter_criteria_match_widget()
            return

        self._mount_no_filter_criteria_match_widget()

    def filter_clear(self) -> None:
        account_collapsibles = list(self.account_collapsibles)

        for account_collapsible in account_collapsibles:
            if account_collapsible.authority_owner == self._initial_account.name:
                account_collapsible.filter_clear()
            else:
                account_collapsible.display = False
        self._remove_no_filter_criteria_match_widget()

    def _mount_no_filter_criteria_match_widget(self) -> None:
        try:
            self.body.query_exactly_one(NoFilterCriteriaMatch)
        except NoMatches:
            self.body.mount(NoFilterCriteriaMatch(items_name="authorities"))

    def _remove_no_filter_criteria_match_widget(self) -> None:
        with contextlib.suppress(NoMatches):
            self.body.query_exactly_one(NoFilterCriteriaMatch).remove()


class AccountCollapsible(CliveCollapsible):
    def __init__(
        self,
        authority: Authority,
        *,
        collapsed: bool = False,
    ) -> None:
        self._authority = authority
        super().__init__(
            *self._create_widgets_to_mount(collapsed=collapsed),
            title=authority.account,
            collapsed=collapsed,
        )

    @property
    def authority_owner(self) -> str:
        return self._authority.account

    def filter(self, selected_accounts_in_filter: list[str], *filter_patterns: str) -> None:
        """
        Update the display based on accounts selected in filter and filter patterns.

        Args:
            selected_accounts_in_filter: Accounts selected in the filter.
            *filter_patterns: Patterns to filter the entries in the authority.
        """

        def update_display_of_authority_roles() -> None:
            """Update the display of authority role widgets within this widget."""
            for authority_role in self.query(AuthorityRole):
                authority_role.filter(*filter_patterns)

        if self._authority.account not in selected_accounts_in_filter:
            self.display = False
            return

        if not filter_patterns:
            self.filter_clear()
            return

        if self._authority.is_matching_pattern(*filter_patterns):
            self.display = True
            update_display_of_authority_roles()
            return
        self.display = False

    def filter_clear(self) -> None:
        """Clear any filters applied to this widget and its children."""
        for authority_role in self.query(AuthorityRole):
            authority_role.filter_clear()
        self.display = True

    def _create_widgets_to_mount(self, *, collapsed: bool) -> list[AuthorityRole]:
        return [AuthorityRole(role, title=role.level_display, collapsed=collapsed) for role in self._authority.roles]


class AuthorityRole(CliveCollapsible):
    def __init__(
        self,
        authority_role: AuthorityRoleRegular | AuthorityRoleMemo,
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

    @property
    def authority_table(self) -> AuthorityTable:
        return self.query_exactly_one(AuthorityTable)

    def filter(self, *filter_patterns: str) -> None:
        """
        Update the display based on filter patterns.

        Args:
            *filter_patterns: Patterns to filter the entries in the authority.
        """

        def update_display_in_authority_table() -> None:
            authority_table = self.authority_table
            authority_table.filter(*filter_patterns)

        if not filter_patterns:
            self.filter_clear()
            return

        matched = self._authority_role.is_matching_pattern(*filter_patterns)
        self.display = matched

        if matched:
            update_display_in_authority_table()

    def filter_clear(self) -> None:
        authority_table = self.authority_table
        authority_table.filter_clear()
        self.display = True

    def _get_right_hand_side_text(self) -> str | None:
        authority_role = self._authority_role
        if authority_role.is_memo:
            return None

        authority_role_regular = authority_role.ensure_regular
        weight_threshold = authority_role_regular.weight_threshold
        imported_weights = authority_role_regular.sum_weights_of_already_imported_keys(self.profile.keys)
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
    Class for items in the authority table.

    Args:
        entry: Object representing the authority entry.
    """

    def __init__(self, entry: AuthorityEntryKeyRegular | AuthorityEntryAccountRegular | AuthorityEntryMemo) -> None:
        self._entry = entry
        super().__init__(*self._create_cells())

    @property
    def entry(self) -> AuthorityEntryKeyRegular | AuthorityEntryAccountRegular | AuthorityEntryMemo:
        return self._entry

    @property
    def entry_value(self) -> str:
        return self._entry.value

    @property
    def stored_keys(self) -> list[PublicKeyAliased]:
        return self.profile.keys.get_all_from_public_key(self.entry_value)

    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        key_or_account_text = self._generate_key_or_account_text()

        if self._entry.is_account:
            action_widget: Widget = Static()
        else:
            stored_keys = self.stored_keys
            action_widget = (
                RemoveKeyAliasButton(*stored_keys)
                if stored_keys
                else ImportPrivateKeyButton(public_key=self._entry.ensure_key.public_key)
            )

        cells = [
            CliveCheckerBoardTableCell(
                key_or_account_text,
                classes="key-or-account" if self._entry.is_weighted else "memo-key",
            )
        ]

        if self._entry.is_weighted:
            cells.append(
                CliveCheckerBoardTableCell(
                    str(self._entry.ensure_weighted.weight),
                    classes="weight",
                )
            )

        cells.append(CliveCheckerBoardTableCell(action_widget, classes="action"))

        return cells

    def _generate_key_or_account_text(self) -> str:
        """
        Generate the text for the key or account cell.

        Returns:
            The text to be displayed in the key or account cell.
        """
        entry_value = self.entry_value
        if self._entry.is_account:
            return entry_value

        aliases = [key.alias for key in self.stored_keys]

        if not aliases or aliases == [entry_value]:
            # by default key is aliased with the public key and we don't want to duplicate
            return entry_value
        if len(aliases) > 1:
            return f"many aliases ({entry_value})"
        return f"{aliases[0]} ({entry_value})"


class AuthorityTable(CliveCheckerboardTable):
    """
    A table containing all entries of a single type of authority.

    Attributes:
        NO_CONTENT_TEXT: Text displayed when there are no entries in the authority.

    Args:
        authority_role: Object representing authority role.
    """

    NO_CONTENT_TEXT = "No entries in authority"

    def __init__(self, authority_role: AuthorityRoleRegular | AuthorityRoleMemo) -> None:
        self._authority_role = authority_role
        super().__init__(header=AuthorityHeader(memo_header=authority_role.is_memo))

    @property
    def authority_items(self) -> DOMQuery[AuthorityItem]:
        return self.query(AuthorityItem)

    def create_static_rows(self) -> Sequence[AuthorityItem]:
        return [AuthorityItem(entry) for entry in self._authority_role.get_entries()]

    def filter(self, *filter_patterns: str) -> None:
        if not filter_patterns:
            self.filter_clear()
            return

        for item in self.authority_items:
            item.display = item.entry.is_matching_pattern(*filter_patterns)
        self.update_cell_colors()

    def filter_clear(self) -> None:
        for item in self.authority_items:
            item.display = True
        self.update_cell_colors()


class AuthorityDetails(TabPane, CliveWidget):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    AUTHORITY_TAB_PANE_TITLE: Final[str] = "Authority"

    def __init__(self, account: TrackedAccount) -> None:
        super().__init__(self.AUTHORITY_TAB_PANE_TITLE)
        self._account = account
        self._authorities: list[Authority] = [account.data.authority for account in self.profile.accounts.tracked]

    @property
    def account_authorities(self) -> AccountsAuthorities:
        return self.query_exactly_one(AccountsAuthorities)

    @property
    def filter_authority(self) -> FilterAuthority:
        return self.query_exactly_one(FilterAuthority)

    async def on_mount(self) -> None:
        self._update_input_suggestions()
        await self.account_authorities.build(self._authorities)
        self._filter_account_authorities()

    def compose(self) -> ComposeResult:
        with Horizontal(id="filter-and-modify"):
            yield FilterAuthority(self._account)
            yield Container(
                CliveButton(label="Modify", variant="success", id_="modify-button", disabled=True),
                id="button-container",
            )
        yield AccountsAuthorities(self._account)

    @on(FilterAuthority.AuthorityFilterReady)
    def _apply_authority_filter(self) -> None:
        """Apply the authority filter based on the input and update the UI."""
        authority_filter_input = self.filter_authority.authority_filter_input
        filter_pattern = authority_filter_input.value_or_error
        all_patterns = []

        if filter_pattern:
            self._update_input_suggestions()
            all_patterns.extend([key.value for key in self.profile.keys.get_by_alias_pattern(filter_pattern)])
            all_patterns.append(filter_pattern)

        self.filter_authority.collapse_account_filter_collapsible()
        self._filter_account_authorities(*all_patterns)

    @on(PrivateKeyActionButton.KeyAliasesChanged)
    async def _rebuild_after_key_aliases_changed(self) -> None:
        await self._rebuild_account_authorities()
        self._apply_authority_filter()

    @on(FilterAuthority.Cleared)
    def _handle_filter_cleared(self) -> None:
        self._update_input_suggestions()
        self.account_authorities.filter_clear()

    @on(FilterAuthority.SelectedAccountsChanged)
    def _handle_selected_accounts_changed(self) -> None:
        self._update_input_suggestions()

    def _filter_account_authorities(self, *filter_patterns: str) -> None:
        self.account_authorities.filter(self.filter_authority.selected_options, *filter_patterns)

    def _update_input_suggestions(self) -> None:
        input_suggestions: set[str] = set()
        filter_authority = self.filter_authority

        options_selected_in_filter = filter_authority.selected_options
        for authority in self._authorities:
            if authority.account in options_selected_in_filter:
                suggestions_to_add = [entry.value for entry in authority.get_entries()]
                input_suggestions.update(suggestions_to_add)

        input_suggestions.update(self.profile.keys.get_all_aliases())
        filter_authority.authority_filter_input.clear_suggestions()
        filter_authority.authority_filter_input.add_suggestion(*input_suggestions)

    async def _rebuild_account_authorities(self) -> None:
        with self.app.batch_update():
            await self.account_authorities.rebuild(self._authorities)

            # somehow after mounting widgets inside account authorities body scroll is moved down, so focus
            # first mounted account collapsible title (and move the scroll by it) then refocus previously
            # focused widget.
            previously_focused = self.app.focused
            all_account_collapsible_titles = self.query(CollapsibleTitle)
            if all_account_collapsible_titles:
                all_account_collapsible_titles.first().focus()
                if previously_focused:
                    previously_focused.focus()
