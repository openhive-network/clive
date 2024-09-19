from __future__ import annotations

import re
from typing import TYPE_CHECKING, Final, Sequence

from textual import on
from textual.binding import Binding
from textual.containers import Center, Horizontal
from textual.widgets import Static, TabPane

from clive.__private.core.accounts.account_manager import AccountManager
from clive.__private.ui.widgets.buttons.page_switch_buttons import PageDownButton, PageUpButton
from clive.__private.ui.widgets.buttons.search_operation_buttons import ClearButton, SearchButton
from clive.__private.ui.widgets.clive_basic import (
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.inputs.account_name_pattern_input import AccountNamePatternInput
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section_title import SectionTitle

if TYPE_CHECKING:
    from textual.app import ComposeResult


class BadAccountsTable(CliveCheckerboardTable):
    """Table for a bad accounts."""

    DEFAULT_CSS = """
    BadAccountsTable {
        width: 1fr;

        #bad-accounts-header {
            height: 1;
            background: $error;
            text-style: bold;
        }

        #bad-accounts-title {
            height: 1;

            OneLineButton {
                width: 1fr;
                min-width: 1;
            }

            SectionTitle {
                width: 3fr;
            }
        }

        Static {
            text-align: center;
            width: 1fr;
        }
    }
    """
    BINDINGS = [
        Binding("pagedown", "next_page", "PgDn"),
        Binding("pageup", "previous_page", "PgUp"),
    ]

    MAX_ACCOUNTS_ON_PAGE: Final[int] = 21
    FIRST_PAGE_INDEX: Final[int] = 0

    def __init__(self) -> None:
        self._page_up_button = PageUpButton()
        self._page_down_button = PageDownButton()
        self._page_up_button.visible = False

        super().__init__(
            header=Static("Account name", id="bad-accounts-header"),
            title=Horizontal(
                self._page_up_button, SectionTitle("Bad accounts"), self._page_down_button, id="bad-accounts-title"
            ),
        )
        self._current_page_index = self.FIRST_PAGE_INDEX
        self._bad_account_names = AccountManager.BAD_ACCOUNT_NAMES
        """Stored in the attribute as it changes in search mode."""
        self._last_page_index = self._get_last_page_index()
        """It is not stored as a final value because it can be dynamically changed with the `_accounts_list`."""

    def create_static_rows(self) -> Sequence[CliveCheckerboardTableRow]:
        start_index = self._current_page_index * self.MAX_ACCOUNTS_ON_PAGE
        end_index = start_index + self.MAX_ACCOUNTS_ON_PAGE

        return [
            CliveCheckerboardTableRow(CliveCheckerBoardTableCell(account))
            for account in self._bad_account_names[start_index:end_index]
        ]

    @on(PageUpButton.Pressed)
    async def action_previous_page(self) -> None:
        if self._current_page_index == self.FIRST_PAGE_INDEX:
            return

        self._current_page_index -= 1
        self._page_down_button.visible = True

        if self._current_page_index <= self.FIRST_PAGE_INDEX:
            self._page_up_button.visible = False

        await self._rebuild_rows()

    @on(PageDownButton.Pressed)
    async def action_next_page(self) -> None:
        if self._current_page_index == self._last_page_index:
            return

        self._current_page_index += 1
        self._page_up_button.visible = True

        if self._current_page_index >= self._last_page_index:
            self._page_down_button.visible = False

        await self._rebuild_rows()

    async def set_search_mode(self, pattern: str) -> None:
        pattern = rf"^{pattern}"
        self._bad_account_names = [
            account for account in AccountManager.BAD_ACCOUNT_NAMES if re.match(pattern, account)
        ]

        await self._reset_table()

    async def set_full_list_mode(self) -> None:
        self._bad_account_names = AccountManager.BAD_ACCOUNT_NAMES

        await self._reset_table()

    def _get_last_page_index(self) -> int:
        return len(self._bad_account_names) // self.MAX_ACCOUNTS_ON_PAGE

    async def _reset_table(self) -> None:
        self._current_page_index = self.FIRST_PAGE_INDEX
        self._last_page_index = self._get_last_page_index()
        self._page_up_button.visible = False
        self._page_down_button.visible = True

        await self._rebuild_rows()

    async def _rebuild_rows(self) -> None:
        with self.app.batch_update():
            await self._remove_rows()
            await self._mount_new_rows()

    async def _remove_rows(self) -> None:
        await self.query(CliveCheckerboardTableRow).remove()
        await self.query(NoContentAvailable).remove()

    async def _mount_new_rows(self) -> None:
        if len(self._bad_account_names) == 0:
            await self.mount(NoContentAvailable("No bad accounts found with this pattern"))
            return

        new_rows = self.create_static_rows()
        self._set_evenness_styles(new_rows)
        await self.mount_all(new_rows)


class BadAccounts(TabPane):
    """Currently only used to display the list of bad accounts (cannot be modified)."""

    DEFAULT_CSS = """
    BadAccounts {
        Center {
            height: auto;
        }

        #scrollable-center {
            max-height: 24;
            height: 1fr;
        }

        ScrollablePart {
            width: 40%;
        }

        #search-controls {
            width: 70%;
            height: 3;

            CliveButton {
                margin: 0 1;
            }
        }
    }
    """
    TITLE: Final[str] = "Bad accounts"

    def __init__(self) -> None:
        super().__init__(title=self.TITLE)

    def compose(self) -> ComposeResult:
        with Center(id="scrollable-center"), ScrollablePart():
            yield BadAccountsTable()

        with Center(), Horizontal(id="search-controls"):
            yield AccountNamePatternInput(required=False, always_show_title=True)
            yield SearchButton()
            yield ClearButton()

    @on(SearchButton.Pressed)
    async def search_pattern_in_list(self) -> None:
        pattern = self.query_one(AccountNamePatternInput).value_or_none()
        if pattern is None:
            return

        await self.query_one(BadAccountsTable).set_search_mode(pattern)

    @on(ClearButton.Pressed)
    async def clear_from_searched(self) -> None:
        await self.query_one(BadAccountsTable).set_full_list_mode()
        self.query_one(AccountNamePatternInput).input.clear()