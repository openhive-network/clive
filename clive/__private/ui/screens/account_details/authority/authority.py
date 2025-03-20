from __future__ import annotations

from typing import TYPE_CHECKING, Final, Sequence

from textual.containers import Container, Horizontal
from textual.widgets import Collapsible, SelectionList, Static, TabPane
from textual.widgets._selection_list import Selection

from clive.__private.core.constants.tui.class_names import CLIVE_EVEN_COLUMN_CLASS_NAME, CLIVE_ODD_COLUMN_CLASS_NAME
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.buttons import CancelButton, CloseOneLineButton, ConfirmButton, ConfirmOneLineButton
from clive.__private.ui.widgets.clive_basic import (
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.inputs.authority_input import AuthorityInput
from clive.__private.ui.widgets.section import SectionBody, SectionScrollable
from wax.models.authority import WaxAuthority
from wax.models.basic import PublicKey
from wax.wax_factory import create_hive_chain
from wax.wax_options import WaxChainOptions

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from wax.models.authority import WaxAccountAuthorityInfo


class AuthorityRoles(SectionScrollable):
    """Widget for storing all AccountCollapsibles."""

    def __init__(self) -> None:
        super().__init__("Authority roles")


class AuthorityType(Collapsible):
    def __init__(self, account_authorities: WaxAuthority | PublicKey | None, title: str) -> None:
        super().__init__(AuthorityTable(account_authorities), title=title)


class AccountCollapsible(Collapsible):
    def __init__(self, authority: WaxAccountAuthorityInfo) -> None:
        super().__init__(
            AuthorityType(authority.authorities.owner, "owner"),
            AuthorityType(authority.authorities.active, "active"),
            AuthorityType(authority.authorities.posting, "posting"),
            AuthorityType(authority.memo_key, "memo key"),
            title=authority.account,
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
        return [
            CliveCheckerBoardTableCell(self._key_or_account, classes="key-or-account"),
            CliveCheckerBoardTableCell(str(self._weight), classes="weight"),
            CliveCheckerBoardTableCell(
                Static()
                if self._is_account_entry
                else (
                    CloseOneLineButton(label="Remove")
                    if self._key_or_account in self.profile.keys
                    else ConfirmOneLineButton("Add")
                ),
                classes="action",
            ),
        ]


class MemoItem(CliveCheckerboardTableRow):
    def __init__(self, memo_key: PublicKey) -> None:
        self._memo_key = memo_key
        super().__init__(*self._create_cells())

    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        return [
            CliveCheckerBoardTableCell(self._memo_key, classes="memo-key"),
            CliveCheckerBoardTableCell(
                CloseOneLineButton(label="Remove")
                if self._memo_key in self.profile.keys
                else ConfirmOneLineButton("Add"),
                classes="action",
            ),
        ]


class AuthorityTable(CliveCheckerboardTable):
    """A table containing all entries of a single type of authority."""

    NO_CONTENT_TEXT = "No entries in authority"

    def __init__(self, single_authority: WaxAuthority | PublicKey | None) -> None:
        self._single_authority = single_authority
        self._is_authority_memo = False
        if single_authority and isinstance(single_authority, PublicKey):
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

        key_rows = [AuthorityItem({key_entry: key_entries[key_entry]}) for key_entry in key_entries]
        account_rows = [
            AuthorityItem({account_entry: account_entries[account_entry]}) for account_entry in account_entries
        ]
        return key_rows + account_rows


class FilterAuthority(Horizontal, CliveWidget):
    BORDER_TITLE = "Filter authority"

    def __init__(self) -> None:
        super().__init__()
        self._filter_entries = [Selection("All", "All")] + [
            Selection(f"{account.name}", f"{account.name}") for account in self.profile.accounts.tracked
        ]

    def compose(self) -> ComposeResult:
        yield AuthorityInput()
        with Collapsible(title="Authority owner account: "):
            yield SelectionList[str](
                *self._filter_entries
            )  # TODO: POSSIBLE BUG IN TEXTUAL: WITH AUTO NOT WORKS PROPERLY
        yield ConfirmButton(label="Search")
        yield CancelButton(label="Clear")

    @property
    def selected_accounts(self) -> list[str]:
        return self.query_exactly_one(SelectionList).selected


class Authority(TabPane, CliveWidget):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    AUTHORITY_TAB_PANE_TITLE: Final[str] = "Authority"

    def __init__(self) -> None:
        super().__init__(self.AUTHORITY_TAB_PANE_TITLE)
        self._all_authorities: list[WaxAccountAuthorityInfo] = []
        chain_id = self.profile.chain_id
        assert chain_id is not None, "Chain id can't be None in order to use wax interface."
        wax_chain_options = WaxChainOptions(chain_id=chain_id, endpoint_url=self.profile.node_address)
        self._wax_interface = create_hive_chain(wax_chain_options)

    async def on_mount(self) -> None:
        tracked_accounts = self.profile.accounts.tracked
        for account in tracked_accounts:
            self._all_authorities.append(await self._wax_interface.collect_account_authorities(account.name))

        authority_roles_body = self.query_exactly_one(SectionBody)
        await authority_roles_body.mount_all([AccountCollapsible(authority) for authority in self._all_authorities])

    def compose(self) -> ComposeResult:
        with Horizontal(id="filter-and-modify"):
            yield FilterAuthority()
            yield Container(ConfirmButton(label="Modify", id_="modify-button"), id="button-container")
        yield AuthorityRoles()
