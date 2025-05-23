from __future__ import annotations

import re
from typing import TYPE_CHECKING, Final, Literal

from textual import on
from textual.containers import Container, Horizontal
from textual.message import Message
from textual.widgets import Collapsible, SelectionList, Static, TabPane
from textual.widgets._collapsible import CollapsibleTitle
from textual.widgets._selection_list import Selection

from clive.__private.core.constants.tui.class_names import CLIVE_EVEN_COLUMN_CLASS_NAME, CLIVE_ODD_COLUMN_CLASS_NAME
from clive.__private.core.iwax import calculate_public_key
from clive.__private.core.keys import PrivateKey, PublicKey
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.buttons import (
    ClearButton,
    CliveButton,
    OneLineButton,
    SearchButton,
)
from clive.__private.ui.widgets.clive_basic import (
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.inputs.authority_input import AuthorityInput
from clive.__private.ui.widgets.inputs.clive_input import CliveInput
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from clive.__private.ui.widgets.section import SectionBody, SectionScrollable
from wax.models.authority import WaxAuthority

if TYPE_CHECKING:
    from collections.abc import Sequence

    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.keys.key_manager import KeyManager
    from clive.__private.ui.widgets.buttons.clive_button import CliveButtonVariant
    from wax.models.authority import WaxAccountAuthorityInfo


def is_match(text: str, pattern: str | list[str]) -> bool:
    def generate_regex_pattern(pattern: str) -> str:
        escaped_pattern = re.escape(pattern)
        return rf".*{escaped_pattern}.*"

    if isinstance(pattern, list):
        return any(re.match(generate_regex_pattern(single_pattern), text) for single_pattern in pattern)
    return bool(re.match(generate_regex_pattern(pattern), text))


def collect_all_entries_from_wax_account_authority_info_object(authority: WaxAccountAuthorityInfo) -> list[str]:
    all_entries = [authority.memo_key]
    for authority_type in ["owner", "active", "posting"]:
        wax_authority = getattr(authority.authorities, authority_type)
        all_entries = all_entries + collect_all_entries_from_wax_authority_object(wax_authority)
    return all_entries


def collect_all_entries_from_wax_authority_object(authority: WaxAuthority) -> list[str]:
    return list(authority.account_auths.keys()) + list(authority.key_auths.keys())


def collect_weights_from_wax_authority_object(authority: WaxAuthority, keys: KeyManager) -> list[int]:
    """Collect weights from WaxAuthority object for keys that are present in the KeyManager."""
    key_auths = authority.key_auths
    return [key_auths[key] for key in list(key_auths.keys()) if key in keys]


def is_wax_account_authority_info_object_has_entry_that_matches_pattern(
    authority: WaxAccountAuthorityInfo, pattern: str | list[str]
) -> bool:
    """Check if given pattern or any of the patterns are present in WaxAccountAuthorityInfo object."""
    if is_match(authority.memo_key, pattern):
        return True
    for authority_type in ["owner", "active", "posting"]:
        wax_authority = getattr(authority.authorities, authority_type)
        if is_wax_authority_object_has_entry_that_matches_pattern(wax_authority, pattern):
            return True
    return False


def is_wax_authority_object_has_entry_that_matches_pattern(authority: WaxAuthority, pattern: str | list[str]) -> bool:
    """Check if the given pattern or any of the patterns are present in the WaxAuthority object."""
    for entry in list(authority.account_auths.keys()) + list(authority.key_auths.keys()):
        if is_match(entry, pattern):
            return True
    return False


class PrivateKeyActionButton(OneLineButton):
    class KeyAliasesChanged(Message):
        """Message sent when key aliases in KeyManager were modified."""

    def __init__(self, label: TextType, variant: CliveButtonVariant, public_key: PublicKey) -> None:
        super().__init__(label, variant)
        self._public_key = public_key

    @property
    def public_key(self) -> PublicKey:
        return self._public_key

    def _key_aliases_changed_callback(self, confirm: bool | None) -> None:
        if confirm:
            self.post_message(self.KeyAliasesChanged())


class ImportPrivateKeyButton(PrivateKeyActionButton):
    class Pressed(PrivateKeyActionButton.Pressed):
        """Message sent when ImportPrivateKeyButton is pressed."""

    def __init__(self, public_key: PublicKey) -> None:
        super().__init__("Import key", "success", public_key)

    @on(Pressed)
    def add_private_key(self, event: ImportPrivateKeyButton.Pressed) -> None:
        from clive.__private.ui.screens.config.manage_key_aliases.new_key_alias import NewKeyAlias

        assert isinstance(event.button, ImportPrivateKeyButton), "Incompatible type of button."
        public_key = event.button.public_key
        self.app.push_screen(NewKeyAlias(public_key_to_validate=public_key), self._key_aliases_changed_callback)


class RemovePrivateKeyButton(PrivateKeyActionButton):
    class Pressed(PrivateKeyActionButton.Pressed):
        """Message sent when RemovePrivateKeyButton is pressed."""

    def __init__(self, public_key: PublicKey) -> None:
        super().__init__("Remove", "error", public_key)

    @on(Pressed)
    def remove_private_key(self, event: RemovePrivateKeyButton.Pressed) -> None:
        from clive.__private.ui.dialogs import RemoveKeyAliasDialog

        assert isinstance(event.button, RemovePrivateKeyButton), "Incompatible type of button."
        public_key = event.button.public_key
        self.app.push_screen(RemoveKeyAliasDialog(public_key=public_key), self._key_aliases_changed_callback)


class AuthorityRoles(SectionScrollable):
    """Widget for storing all AccountCollapsibles."""

    def __init__(self) -> None:
        super().__init__("Authority roles")

    @property
    def body(self) -> SectionBody:
        return self.query_exactly_one(SectionBody)

    async def rebuild(
        self, filtered_authorities: list[WaxAccountAuthorityInfo], filter_pattern: str | list[str] | None = None
    ) -> None:
        body = self.body

        widgets: list[AccountCollapsible] | list[NoContentAvailable] = []
        await body.query("*").remove()
        if not filtered_authorities:
            widgets = [NoContentAvailable("There are no authorities that match filter criteria.")]
        else:
            widgets = [
                AccountCollapsible(authority, filter_pattern=filter_pattern) for authority in filtered_authorities
            ]

        await body.mount_all(widgets)


class AccountCollapsible(Collapsible):
    def __init__(
        self,
        authority: WaxAccountAuthorityInfo,
        *,
        initial_mount: bool = False,
        filter_pattern: str | list[str] | None = None,
        collapsed: bool = False,
    ) -> None:
        widgets_to_mount = []

        for authority_type in ["owner", "active", "posting"]:
            wax_authority = getattr(authority.authorities, authority_type)
            if filter_pattern:
                if is_wax_authority_object_has_entry_that_matches_pattern(wax_authority, filter_pattern):
                    widgets_to_mount.append(
                        AuthorityType(wax_authority, title=authority_type, filter_pattern=filter_pattern)
                    )
            else:
                widgets_to_mount.append(AuthorityType(wax_authority, title=authority_type, collapsed=initial_mount))

        memo_key = authority.memo_key
        if filter_pattern:
            if is_match(memo_key, filter_pattern):
                widgets_to_mount.append(AuthorityType(memo_key, title="memo key"))
        else:
            widgets_to_mount.append(AuthorityType(memo_key, title="memo key", collapsed=initial_mount))

        super().__init__(*widgets_to_mount, title=authority.account, collapsed=collapsed)


class AuthorityType(Collapsible, CliveWidget):
    def __init__(
        self,
        account_authorities: WaxAuthority | str | None,
        *,
        title: str,
        filter_pattern: str | list[str] | None = None,
        collapsed: bool = False,
    ) -> None:
        super().__init__(
            AuthorityTable(account_authorities, filter_pattern=filter_pattern), title=title, collapsed=collapsed
        )
        self._weight_threshold = None
        if account_authorities and isinstance(account_authorities, WaxAuthority):
            self._weight_threshold = account_authorities.weight_threshold
            self._collected_weights = collect_weights_from_wax_authority_object(account_authorities, self.profile.keys)

    def compose(self) -> ComposeResult:
        yield Horizontal(
            self._title,
            Container(
                Static(
                    f"imported weights: {sum(self._collected_weights)}, threshold: {self._weight_threshold}"
                    if self._weight_threshold
                    else "",
                    id="threshold-and-weights",
                )
            ),
        )
        yield self.Contents(*self._contents_list)


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
    def __init__(self, entry: dict[str, int]) -> None:
        assert len(entry) == 1, "Entry of AuthorityItem should have one key and corresponding value."
        self._key_or_account = next(iter(entry.keys()))
        self._weight = entry[self._key_or_account]
        self._is_account_entry = not self._key_or_account.startswith("STM")
        super().__init__(*self._create_cells())

    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        key_or_account_text = self._key_or_account

        if not self._is_account_entry and self._key_or_account in self.profile.keys:
            alias = self.profile.keys.get_from_public_key(self._key_or_account).alias
            if alias != self._key_or_account:
                key_or_account_text = f"{alias} ({self._key_or_account})"

        return [
            CliveCheckerBoardTableCell(key_or_account_text, classes="key-or-account"),
            CliveCheckerBoardTableCell(str(self._weight), classes="weight"),
            CliveCheckerBoardTableCell(
                Static()
                if self._is_account_entry
                else (
                    RemovePrivateKeyButton(PublicKey(value=self._key_or_account))
                    if self._key_or_account in self.profile.keys
                    else ImportPrivateKeyButton(PublicKey(value=self._key_or_account))
                ),
                classes="action",
            ),
        ]


class MemoItem(CliveCheckerboardTableRow):
    def __init__(self, memo_key: str) -> None:
        self._memo_key = memo_key
        super().__init__(*self._create_cells())

    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        memo_key_text = self._memo_key

        if self._memo_key in self.profile.keys:
            alias = self.profile.keys.get_from_public_key(self._memo_key).alias
            if alias != self._memo_key:
                memo_key_text = f"{alias} ({self._memo_key})"

        return [
            CliveCheckerBoardTableCell(memo_key_text, classes="memo-key"),
            CliveCheckerBoardTableCell(
                RemovePrivateKeyButton(PublicKey(value=self._memo_key))
                if self._memo_key in self.profile.keys
                else ImportPrivateKeyButton(PublicKey(value=self._memo_key)),
                classes="action",
            ),
        ]


class AuthorityTable(CliveCheckerboardTable):
    """A table containing all entries of a single type of authority."""

    NO_CONTENT_TEXT = "No entries in authority"

    def __init__(self, single_authority: WaxAuthority | str | None, filter_pattern: str | list[str] | None) -> None:
        self._single_authority = single_authority
        self._filter_pattern = filter_pattern
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

        if self._filter_pattern:
            key_entries = {
                entry: self._single_authority.key_auths[entry]
                for entry in self._single_authority.key_auths
                if is_match(entry, self._filter_pattern)
            }
            account_entries = {
                entry: self._single_authority.account_auths[entry]
                for entry in self._single_authority.account_auths
                if is_match(entry, self._filter_pattern)
            }
        else:
            key_entries = self._single_authority.key_auths
            account_entries = self._single_authority.account_auths
        key_rows = [AuthorityItem({key_entry: key_entries[key_entry]}) for key_entry in key_entries]
        account_rows = [
            AuthorityItem({account_entry: account_entries[account_entry]}) for account_entry in account_entries
        ]

        return key_rows + account_rows


class AccountSelectionList(SelectionList[str], CliveWidget):
    """Selection list with account names for filtering authorities."""

    def __init__(self, account: TrackedAccount) -> None:
        self._initial_checked_account_name = account.name
        working_account_name = self.profile.accounts.working.name if self.profile.accounts.working_or_none else None
        self._filter_entries = [Selection("all", "all")] + [
            Selection(
                f"{tracked_account.name}{
                    ' (working)' if working_account_name and tracked_account.name is working_account_name else ''
                }",
                tracked_account.name,
                initial_state=tracked_account.name is self._initial_checked_account_name,
            )
            for tracked_account in self.profile.accounts.tracked
        ]
        super().__init__(*self._filter_entries)

    def restore_default(self) -> None:
        self.deselect_all()
        all_selections = [self.get_option_at_index(index) for index in range(len(self.profile.accounts.tracked) + 1)]
        for selection in all_selections:
            if selection.value == self._initial_checked_account_name:
                self.select(selection)

    @on(SelectionList.SelectionToggled)
    def _handle_options_in_filter(self, event: AccountSelectionList.SelectionToggled[str]) -> None:
        def change_every_option_except_all_option(*, action: Literal["select", "deselect"]) -> None:
            for selection in all_selections:
                if selection.value != "all":
                    selection_list.select(selection) if action == "select" else selection_list.deselect(selection)

        index = event.selection_index
        selection_list = event.selection_list
        option_toggled = selection_list.get_option_at_index(index)
        all_selections = [
            selection_list.get_option_at_index(index) for index in range(len(self.profile.accounts.tracked) + 1)
        ]

        if option_toggled.value == "all":
            if "all" in selection_list.selected:
                change_every_option_except_all_option(action="select")
            else:
                change_every_option_except_all_option(action="deselect")
        else:
            selection_for_all_accounts = selection_list.get_option_at_index(0)
            if "all" in selection_list.selected:
                selection_list.deselect(selection_for_all_accounts)


class AccountFilterCollapsible(Collapsible):
    BORDER_TITLE = " Authority for accounts "

    def __init__(self, initial_title: str) -> None:
        super().__init__(title=initial_title)
        self._initial_title = initial_title

    def restore_title(self) -> None:
        self.title = self._initial_title

    def update_title(self, selected_accounts: list[str]) -> None:
        if len(selected_accounts) == 1 or (len(selected_accounts) == 2 and "all" in selected_accounts):  # noqa: PLR2004
            self.title = next(iter(selected_accounts))
        elif len(selected_accounts) == 0:
            self.title = "no selected accounts"
        else:
            self.title = "multiple"


class FilterAuthority(Horizontal, CliveWidget):
    class AuthorityFilterReady(Message):
        """Message sent when authority filter is ready to be applied."""

    class Cleared(Message):
        """Message sent when authority filter was restored to default."""

    class InputPatternReapplied(Message):
        """Message sent when filter pattern from input was overridden."""

    class SelectedAccountsChanged(Message):
        """Message sent when selected accounts in AccountSelectionList were changed."""

    BORDER_TITLE = "Filter authority"

    def __init__(self, account: TrackedAccount) -> None:
        super().__init__()
        self._account = account
        self._pattern_filter_applied: bool = False

    def compose(self) -> ComposeResult:
        yield AuthorityInput()
        with AccountFilterCollapsible(initial_title=self._account.name):
            yield AccountSelectionList(self._account)
        yield SearchButton()
        yield ClearButton()

    @property
    def account_filter_collapsible(self) -> AccountFilterCollapsible:
        return self.query_exactly_one(AccountFilterCollapsible)

    @property
    def account_selection_list(self) -> AccountSelectionList:
        return self.query_exactly_one(AccountSelectionList)

    @property
    def selected_options(self) -> list[str]:
        return self.account_selection_list.selected

    @property
    def authority_input(self) -> AuthorityInput:
        return self.query_exactly_one(AuthorityInput)

    @on(AccountSelectionList.SelectionToggled)
    def account_toggled(self, event: AccountSelectionList.SelectionToggled[str]) -> None:
        self.account_filter_collapsible.update_title(event.selection_list.selected)
        self.post_message(self.SelectedAccountsChanged())

    @on(SearchButton.Pressed)
    def request_authority_filter_by_button(self) -> None:
        self._request_authority_filter()

    @on(CliveInput.Submitted)
    def request_authority_filter_by_event(self) -> None:
        self._request_authority_filter()

    @on(ClearButton.Pressed)
    async def clear_filters(self) -> None:
        self.apply_default_filter()
        self.post_message(self.SelectedAccountsChanged())
        self.post_message(self.Cleared())
        self._pattern_filter_applied = False

    def apply_default_filter(self) -> None:
        self.authority_input.clear_validation()
        self.account_selection_list.restore_default()
        self.account_filter_collapsible.restore_title()
        self.collapse_account_filter_collapsible()

    def collapse_account_filter_collapsible(self) -> None:
        self.account_filter_collapsible.collapsed = True

    def _request_authority_filter(self) -> None:
        if self._pattern_filter_applied:
            self.post_message(self.InputPatternReapplied())
        self.post_message(self.AuthorityFilterReady())
        self._pattern_filter_applied = True


class Authority(TabPane, CliveWidget):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    AUTHORITY_TAB_PANE_TITLE: Final[str] = "Authority"

    def __init__(self, account: TrackedAccount) -> None:
        super().__init__(self.AUTHORITY_TAB_PANE_TITLE)
        self._account = account
        self._authorities: list[WaxAccountAuthorityInfo] = []
        self._filtered_authorities: list[WaxAccountAuthorityInfo] = []
        self._authority_roles = AuthorityRoles()

    async def on_mount(self) -> None:
        tracked_accounts = self.profile.accounts.tracked

        for account in tracked_accounts:
            account_authority = (
                await self.world.commands.collect_account_authorities(account_name=account.name)
            ).result_or_raise
            self._authorities.append(account_authority)

        self._update_filtered_authorities_and_input_suggestions()

        await self._authority_roles.body.mount_all(
            [AccountCollapsible(authority, initial_mount=True) for authority in self._filtered_authorities]
        )

    def compose(self) -> ComposeResult:
        with Horizontal(id="filter-and-modify"):
            yield FilterAuthority(self._account)
            yield Container(
                CliveButton(label="Modify", variant="success", id_="modify-button", disabled=True),
                id="button-container",
            )
        yield self._authority_roles

    @property
    def filter_authority(self) -> FilterAuthority:
        return self.query_exactly_one(FilterAuthority)

    @on(FilterAuthority.AuthorityFilterReady)
    async def _apply_authority_filter(self) -> None:
        authority_input = self.query_exactly_one(AuthorityInput)
        filter_pattern = authority_input.value_or_none()
        if filter_pattern:
            valid_private = PrivateKey.is_valid(filter_pattern)
            if valid_private:
                filter_pattern = calculate_public_key(filter_pattern).value
                self.notify("Private key converted to public while searching.")

            alias_patterns = [
                aliased_key.value for aliased_key in self.profile.keys if is_match(aliased_key.alias, filter_pattern)
            ]
            multiple_patterns = [*alias_patterns, filter_pattern]
            # filtered_authorities variable is already filtered for accounts
            authorities_that_match_pattern = [
                authority
                for authority in self._filtered_authorities
                if is_wax_account_authority_info_object_has_entry_that_matches_pattern(authority, multiple_patterns)
            ]
            self._filtered_authorities = authorities_that_match_pattern

        self.filter_authority.collapse_account_filter_collapsible()
        await self._rebuild_authority_roles(multiple_patterns if "multiple_patterns" in locals() else filter_pattern)

    @on(PrivateKeyActionButton.KeyAliasesChanged)
    async def rebuild_after_key_aliases_changed(self) -> None:
        await self._rebuild_authority_roles()

    @on(FilterAuthority.Cleared)
    async def rebuild_after_clearing_authority_filter(self) -> None:
        await self._rebuild_authority_roles()

    @on(FilterAuthority.InputPatternReapplied)
    def update_authorities_and_suggestions_after_input_pattern_from_filter_was_reapplied(self) -> None:
        self._update_filtered_authorities_and_input_suggestions()

    @on(FilterAuthority.SelectedAccountsChanged)
    def _update_authorities_and_suggestions_after_account_in_filter_changed(self) -> None:
        self._update_filtered_authorities_and_input_suggestions()

    def _update_filtered_authorities_and_input_suggestions(self) -> None:
        """Filter authorities for selected accounts in AccountSelectionList and update input suggestions."""
        self._filtered_authorities.clear()
        input_suggestions = []

        filter_authority = self.filter_authority

        options_selected_in_filter = filter_authority.selected_options
        for authority in self._authorities:
            if authority.account in options_selected_in_filter:
                self._filtered_authorities.append(authority)
                for collected_entry in collect_all_entries_from_wax_account_authority_info_object(authority):
                    if collected_entry not in input_suggestions:
                        input_suggestions.append(collected_entry)

        input_suggestions.extend(self.profile.keys.get_all_aliases())
        filter_authority.authority_input.load_new_suggestions(input_suggestions)

    async def _rebuild_authority_roles(self, filter_pattern: str | list[str] | None = None) -> None:
        with self.app.batch_update():
            await self._authority_roles.rebuild(self._filtered_authorities, filter_pattern)

            # somehow after mounting widgets inside authority roles body scroll is moved down, so focus first mounted
            # account collapsible title (and move the scroll by it) then refocus previously focused widget.
            previously_focused = self.app.focused
            all_account_collapsible_titles = self.query(CollapsibleTitle)
            if all_account_collapsible_titles:
                all_account_collapsible_titles.first().focus()
                if previously_focused:
                    previously_focused.focus()
