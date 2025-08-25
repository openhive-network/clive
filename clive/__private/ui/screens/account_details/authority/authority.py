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
from clive.__private.ui.dialogs import NewKeyAliasDialog
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
    """A wrapper to provide utility methods for WaxAccountAuthorityInfo and WaxAuthority objects."""

    def __init__(self, authority: WaxAccountAuthorityInfo | WaxAuthority) -> None:
        self._authority = authority

    def collect_all_entries(self) -> list[str]:
        if isinstance(self._authority, WaxAccountAuthorityInfo):
            all_entries = [self._authority.memo_key]
            for authority_type in ["owner", "active", "posting"]:
                wax_authority = getattr(self._authority.authorities, authority_type)
                all_entries = all_entries + self._get_account_and_key_auths(wax_authority)
        else:
            all_entries = self._get_account_and_key_auths(self._authority)
        return all_entries

    def collect_weights(self, keys: KeyManager) -> list[int]:
        """Collect weights for keys that are present in the KeyManager."""
        weights: list[int] = []
        if isinstance(self._authority, WaxAccountAuthorityInfo):
            for authority_type in ["owner", "active", "posting"]:
                wax_authority = getattr(self._authority.authorities, authority_type)
                weights = weights + [
                    wax_authority.key_auths[key] for key in list(wax_authority.key_auths.keys()) if key in keys
                ]
        else:
            weights = [self._authority.key_auths[key] for key in list(self._authority.key_auths.keys()) if key in keys]
        return weights

    def is_object_has_entry_that_matches_pattern(self, *patterns: str) -> bool:
        return any(is_match(entry, *patterns) for entry in self.collect_all_entries())

    @staticmethod
    def _get_account_and_key_auths(authority: WaxAuthority) -> list[str]:
        return list(authority.account_auths.keys()) + list(authority.key_auths.keys())


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
    def add_private_key(self, event: ImportPrivateKeyButton.Pressed) -> None:
        assert isinstance(event.button, ImportPrivateKeyButton), "Incompatible type of button."
        public_key = event.button._public_key
        self.app.push_screen(NewKeyAliasDialog(public_key), self._key_aliases_changed_callback)


class RemovePrivateKeyButton(PrivateKeyActionButton):
    class Pressed(PrivateKeyActionButton.Pressed):
        """Message sent when RemovePrivateKeyButton is pressed."""

    def __init__(self, key_alias: str) -> None:
        super().__init__("Remove", "error")
        self._key_alias = key_alias

    @on(Pressed)
    def remove_private_key(self, event: RemovePrivateKeyButton.Pressed) -> None:
        from clive.__private.ui.dialogs import RemoveKeyAliasDialog  # noqa: PLC0415

        assert isinstance(event.button, RemovePrivateKeyButton), "Incompatible type of button."
        self.app.push_screen(RemoveKeyAliasDialog(key_alias=self._key_alias), self._key_aliases_changed_callback)


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


class AccountCollapsible(CliveCollapsible):
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


class AuthorityType(CliveCollapsible):
    def __init__(
        self,
        account_authorities: WaxAuthority | str | None,
        *,
        title: str,
        filter_pattern: str | list[str] | None = None,
        collapsed: bool = False,
    ) -> None:
        self._weight_threshold = None
        right_hand_side_text = None
        if account_authorities and isinstance(account_authorities, WaxAuthority):
            self._weight_threshold = account_authorities.weight_threshold
            collected_weights = WaxAuthorityWrapper(account_authorities).collect_weights(self.profile.keys)
            right_hand_side_text = f"imported weights: {sum(collected_weights)}, threshold: {self._weight_threshold}"

        super().__init__(
            AuthorityTable(account_authorities, filter_pattern=filter_pattern),
            title=title,
            collapsed=collapsed,
            right_hand_side_text=right_hand_side_text,
        )


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

        return [
            CliveCheckerBoardTableCell(key_or_account_text, classes="key-or-account"),
            CliveCheckerBoardTableCell(str(self._weight), classes="weight"),
            CliveCheckerBoardTableCell(action_widget, classes="action"),
        ]


class MemoItem(CliveCheckerboardTableRow):
    def __init__(self, memo_key: str) -> None:
        self._memo_key = memo_key
        super().__init__(*self._create_cells())

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


class Authority(TabPane, CliveWidget):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    AUTHORITY_TAB_PANE_TITLE: Final[str] = "Authority"

    def __init__(self, account: TrackedAccount) -> None:
        super().__init__(self.AUTHORITY_TAB_PANE_TITLE)
        self._account = account
        self._authorities: list[WaxAccountAuthorityInfo] = []
        self._filtered_authorities: list[WaxAccountAuthorityInfo] = []
        self._authority_roles = AuthorityRoles()
        self._filter_pattern_already_applied: bool = False

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
        authority_input = self.query_exactly_one(AuthorityFilterInput)
        filter_pattern = authority_input.value_or_none()
        if filter_pattern:
            if self._filter_pattern_already_applied:
                self._update_filtered_authorities_and_input_suggestions()

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

        self._filter_pattern_already_applied = bool(filter_pattern)
        self.filter_authority.collapse_account_filter_collapsible()
        await self._rebuild_authority_roles(multiple_patterns if "multiple_patterns" in locals() else filter_pattern)

    @on(PrivateKeyActionButton.KeyAliasesChanged)
    async def rebuild_after_key_aliases_changed(self) -> None:
        await self._rebuild_authority_roles()

    @on(FilterAuthority.Cleared)
    async def rebuild_after_clearing_authority_filter(self) -> None:
        self._update_filtered_authorities_and_input_suggestions()
        await self._rebuild_authority_roles()

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
                for collected_entry in WaxAuthorityWrapper(authority).collect_all_entries():
                    input_suggestions.add(collected_entry)

        input_suggestions.extend(self.profile.keys.get_all_aliases())
        filter_authority.authority_filter_input.clear_suggestions()
        filter_authority.authority_filter_input.add_suggestion(*input_suggestions)

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
