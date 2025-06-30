from __future__ import annotations

import re
from typing import TYPE_CHECKING, Final

from textual import on
from textual.containers import Container, Horizontal
from textual.message import Message
from textual.widgets import Static, TabPane
from textual.widgets._collapsible import CollapsibleTitle

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
from clive.__private.ui.widgets.inputs.authority_filter_input import AuthorityFilterInput
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from clive.__private.ui.widgets.section import SectionBody, SectionScrollable
from wax.complex_operations.account_update import AccountAuthorityUpdateOperation
from wax.models.authority import WaxAuthority

if TYPE_CHECKING:
    from collections.abc import Sequence

    from rich.text import TextType
    from textual.app import ComposeResult
    from textual.widget import Widget

    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.keys.key_manager import KeyManager
    from clive.__private.ui.widgets.buttons.clive_button import CliveButtonVariant


class WaxAuthorityWrapper:
    """A wrapper to provide utility methods for WaxAuthority objects."""

    def __init__(self, authority: WaxAuthority) -> None:
        self._authority = authority

    def collect_all_entries(self) -> list[str]:
        return list(self._authority.account_auths.keys()) + list(self._authority.key_auths.keys())

    def collect_weights(self, keys: KeyManager) -> list[int]:
        """Collect weights for keys that are present in the KeyManager."""
        return [self._authority.key_auths[key] for key in list(self._authority.key_auths.keys()) if key in keys]

    def is_object_has_entry_that_matches_pattern(self, *patterns: str) -> bool:
        return any(is_match(entry, *patterns) for entry in self.collect_all_entries())


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
        self.app.push_screen(NewKeyAliasDialog(public_key_to_match=self._public_key), self._key_aliases_changed_callback)


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

    async def build(self, authority_operations: list[AccountAuthorityUpdateOperation]) -> None:
        await self.body.mount_all([AccountCollapsible(operation) for operation in authority_operations])

    async def rebuild(self, authority_operations: list[AccountAuthorityUpdateOperation]) -> None:
        await self.body.query("*").remove()
        await self.build(authority_operations)

    async def update(self, selected_accounts_in_filter: list[str], *filter_patterns: str) -> None:
        """
        Update the display of AuthorityRoles based on filter patterns selected accounts in filter.

        This method updates each AccountCollapsible inside the body of AuthorityRoles. Also handles NoContentAvailable
        widget.
        """
        results = [
            account_collapsible.update(selected_accounts_in_filter, *filter_patterns)
            for account_collapsible in self.body.query(AccountCollapsible)
        ]
        if any(results):
            await self._remove_no_content_available_widget()
        else:
            self._mount_no_content_available_widget()

    def _mount_no_content_available_widget(self) -> None:
        self.body.mount(NoContentAvailable("There are no authorities that match filter criteria."))

    async def _remove_no_content_available_widget(self) -> None:
        await self.body.query(NoContentAvailable).remove()


class AccountCollapsible(CliveCollapsible):
    def __init__(
        self,
        operation: AccountAuthorityUpdateOperation,
        *,
        collapsed: bool = False,
    ) -> None:
        widgets_to_mount = []

        for role in operation.categories.hive:
            title = role.level if role.level != "memo" else "memo key"
            widgets_to_mount.append(AuthorityType(role.value, title=title, collapsed=collapsed))

        super().__init__(*widgets_to_mount, title=operation.categories.hive.account, collapsed=collapsed)
        self._operation = operation

    @property
    def operation(self) -> AccountAuthorityUpdateOperation:
        return self._operation

    def update(self, selected_accounts_in_filter: list[str], *filter_patterns: str) -> bool:
        """Update the display of AccountCollapsible based on accounts selected in filter and filter patterns."""

        def update_display_of_authority_types() -> None:
            """Update the display of AuthorityType widgets within this AccountCollapsible."""
            for authority_type in self.query(AuthorityType):
                authority_type.update(*filter_patterns)

        if self.operation.categories.hive.account not in selected_accounts_in_filter:
            self.display = False
            return False

        if not filter_patterns:
            self.display = True
            update_display_of_authority_types()
            return True

        for role in self.operation.categories.hive:
            if role.level != "memo":
                if WaxAuthorityWrapper(role.value).is_object_has_entry_that_matches_pattern(*filter_patterns):
                    self.display = True
                    update_display_of_authority_types()
                    return True
            elif is_match(role.value, *filter_patterns):
                self.display = True
                update_display_of_authority_types()
                return True

        self.display = False
        return False


class AuthorityType(CliveCollapsible):
    def __init__(
        self,
        account_authorities: WaxAuthority | str | None,
        *,
        title: str,
        collapsed: bool = False,
    ) -> None:
        self._weight_threshold = None
        right_hand_side_text = None
        if account_authorities and isinstance(account_authorities, WaxAuthority):
            self._weight_threshold = account_authorities.weight_threshold
            collected_weights = WaxAuthorityWrapper(account_authorities).collect_weights(self.profile.keys)
            right_hand_side_text = f"imported weights: {sum(collected_weights)}, threshold: {self._weight_threshold}"

        super().__init__(
            AuthorityTable(account_authorities),
            title=title,
            collapsed=collapsed,
            right_hand_side_text=right_hand_side_text,
        )
        self._account_authorities = account_authorities

    @property
    def authority(self) -> WaxAuthority | str | None:
        return self._account_authorities

    def update(self, *filter_patterns: str) -> None:
        """Update the display of AuthorityType based on filter patterns."""

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

        if isinstance(self._account_authorities, WaxAuthority):
            matched = WaxAuthorityWrapper(self._account_authorities).is_object_has_entry_that_matches_pattern(
                *filter_patterns
            )
        else:
            matched = is_match(self._account_authorities, *filter_patterns)
        self.display = matched

        if matched:
            update_display_in_authority_table()


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
    def __init__(self, key_or_account: str, weight: int) -> None:
        self._key_or_account = key_or_account
        self._weight = weight
        self._is_account_entry = not PublicKey.is_valid(key_or_account)
        super().__init__(*self._create_cells())

    @property
    def entry(self) -> str:
        return self._key_or_account

    @property
    def public_key(self) -> PublicKey:
        assert not self._is_account_entry, "This property is only available for key entries."
        return PublicKey(value=self._key_or_account)

    def update(self, *filter_patterns: str) -> None:
        filter_pattern_present = bool(filter_patterns)
        self.display = is_match(self._key_or_account, *filter_patterns) if filter_pattern_present else True

    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        is_known_key = self._key_or_account in self.profile.keys
        alias = self.profile.keys.get_first_from_public_key(self._key_or_account).alias if is_known_key else None
        key_or_account_text = (
            f"{alias} ({self._key_or_account})" if alias and alias != self._key_or_account else self._key_or_account
        )

        if self._is_account_entry:
            action_widget: Widget = Static()
        elif alias is not None:
            action_widget = RemovePrivateKeyButton(key_alias=alias)
        else:
            action_widget = ImportPrivateKeyButton(PublicKey(value=self._key_or_account))

        action_widget: Widget | None = None

        if self._is_account_entry:
            # we can't add corresponding key to the account, so we just display static widget without text
            action_widget = Static()
        else:
            public_key = self.public_key
            action_widget = (
                RemovePrivateKeyButton(public_key)
                if public_key in self.profile.keys
                else ImportPrivateKeyButton(public_key)
            )

        return [
            CliveCheckerBoardTableCell(key_or_account_text, classes="key-or-account"),
            CliveCheckerBoardTableCell(str(self._weight), classes="weight"),
            CliveCheckerBoardTableCell(action_widget, classes="action"),
        ]


class MemoItem(CliveCheckerboardTableRow):
    def __init__(self, memo_key: str) -> None:
        self._memo_key = memo_key
        super().__init__(*self._create_cells())

    @property
    def entry(self) -> str:
        return self._memo_key

    @property
    def public_key(self) -> PublicKey:
        return PublicKey(value=self._memo_key)

    def update(self, *filter_patterns: str) -> None:
        filter_pattern_present = bool(filter_patterns)
        self.display = is_match(self._memo_key, *filter_patterns) if filter_pattern_present else True

    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        is_known_key = self._memo_key in self.profile.keys
        alias = self.profile.keys.get_first_from_public_key(self._memo_key).alias if is_known_key else None
        memo_key_text = f"{alias} ({self._memo_key})" if alias and alias != self._memo_key else self._memo_key

        if alias is not None:
            action_widget: Widget = RemovePrivateKeyButton(key_alias=alias)
        else:
            action_widget = ImportPrivateKeyButton(PublicKey(value=self._memo_key))
        return [
            CliveCheckerBoardTableCell(memo_key_text, classes="memo-key"),
            CliveCheckerBoardTableCell(
                action_widget,
                classes="action",
            ),
        ]


class AuthorityTable(CliveCheckerboardTable):
    """
    A table containing all entries of a single type of authority.

    Attributes:
        NO_CONTENT_TEXT: Text displayed when there are no entries in the authority.

    Args:
        single_authority: An authority object or a memo key.
        filter_pattern: Patterns to filter the entries in the authority.
    """

    NO_CONTENT_TEXT = "No entries in authority"

    def __init__(self, single_authority: WaxAuthority | str | None) -> None:
        self._single_authority = single_authority
        self._is_authority_memo = False
        if single_authority and isinstance(single_authority, str):
            self._is_authority_memo = True

        super().__init__(header=AuthorityHeader(memo_header=self._is_authority_memo))

    def create_static_rows(self) -> Sequence[AuthorityItem] | Sequence[MemoItem]:
        if not self._single_authority:  # no entries in this type of authority
            return []

        if self._is_authority_memo:
            return [MemoItem(self._single_authority)]

        assert isinstance(self._single_authority, WaxAuthority), "In this place authority has to be WaxAuthority type."

        key_entries = self._single_authority.key_auths
        account_entries = self._single_authority.account_auths

        key_rows = [AuthorityItem(key_entry, weight) for key_entry, weight in key_entries.items()]
        account_rows = [AuthorityItem(account_entry, weight) for account_entry, weight in account_entries.items()]
        return key_rows + account_rows

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
            assert isinstance(row, (AuthorityItem, MemoItem)), "Invalid type of row."
            row.update(*filter_patterns)
            self.update_cell_colors()


class Authority(TabPane, CliveWidget):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    AUTHORITY_TAB_PANE_TITLE: Final[str] = "Authority"

    def __init__(self, account: TrackedAccount) -> None:
        super().__init__(self.AUTHORITY_TAB_PANE_TITLE)
        self._account = account
        self._authority_operations: list[AccountAuthorityUpdateOperation] = []
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

        def get_filter_pattern() -> str | None:
            """Retrieve and process the filter pattern from the authority input."""
            filter_pattern = authority_filter_input.value_or_none()
            if filter_pattern:
                return filter_pattern
            return None

        def handle_existing_filter_pattern() -> None:
            if self._filter_pattern_already_applied:
                self._update_input_suggestions()

        def generate_filter_patterns() -> list[str]:
            assert isinstance(filter_pattern, str), "Filter pattern should be a string."
            alias_patterns = [
                aliased_key.value for aliased_key in self.profile.keys if is_match(aliased_key.alias, filter_pattern)
            ]
            return [*alias_patterns, filter_pattern]

        authority_filter_input = self.query_exactly_one(AuthorityFilterInput)
        filter_pattern = get_filter_pattern()

        if filter_pattern:
            handle_existing_filter_pattern()
            multiple_patterns = generate_filter_patterns()
        else:
            multiple_patterns = []

        self._filter_pattern_already_applied = bool(filter_pattern)
        self.filter_authority.collapse_account_filter_collapsible()
        await self._update_display_inside_authority_roles(*multiple_patterns)

    @on(PrivateKeyActionButton.KeyAliasesChanged)
    async def rebuild_after_key_aliases_changed(self) -> None:
        await self._rebuild_authority_roles()
        await self._apply_authority_filter()

    @on(FilterAuthority.Cleared)
    async def rebuild_after_clearing_authority_filter(self) -> None:
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
            self._authority_operations.append(authority_operation)

    async def _update_display_inside_authority_roles(self, *filter_patterns: str) -> None:
        with self.app.batch_update():
            await self.authority_roles.update(self.filter_authority.selected_options, *filter_patterns)

    def _update_input_suggestions(self) -> None:
        input_suggestions: set[str] = set()
        filter_authority = self.filter_authority

        options_selected_in_filter = filter_authority.selected_options
        for operation in self._authority_operations:
            if operation.categories.hive.account in options_selected_in_filter:
                for role in operation.categories.hive:
                    if role.level != "memo":
                        for key in (role.value.key_auths, role.value.account_auths):
                            suggestions_to_add = list(key.keys())
                            if len(suggestions_to_add) >= 1:
                                input_suggestions.update(suggestions_to_add)
                    else:
                        input_suggestions.add(role.value)

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
